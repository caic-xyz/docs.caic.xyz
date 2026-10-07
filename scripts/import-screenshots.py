#!/usr/bin/env python3
"""Import referenced caic screenshots with recoverable publication and verify catalog provenance."""

import argparse
import fcntl
import hashlib
import json
import re
import shutil
import struct
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "public/screenshots/frontend"
BACKUP = ROOT / ".screenshots-previous"
LOCK = ROOT / ".screenshots-import.lock"
PREFIX = "/screenshots/frontend/"
MAX_TEXT_BYTES = 1024 * 1024


@dataclass(frozen=True)
class Source:
    revision: str
    inputsSha256: str


@dataclass(frozen=True)
class Scenario:
    name: str
    file: str
    width: int
    height: int
    sha256: str
    description: str


@dataclass(frozen=True)
class Catalog:
    schemaVersion: int
    producer: str
    platform: str
    source: Source
    scenarios: list[Scenario]


def read_text(path: Path) -> str:
    """Bound catalogs and page sources to one MiB before decoding."""
    with path.open("rb") as stream:
        content = stream.read(MAX_TEXT_BYTES + 1)
    if len(content) > MAX_TEXT_BYTES:
        raise ValueError(f"text input exceeds one MiB: {path.name}")
    return content.decode("utf-8")


def read_catalog(directory: Path) -> Catalog:
    raw = json.loads(read_text(directory / "manifest.json"))
    catalog = Catalog(
        schemaVersion=raw["schemaVersion"],
        producer=raw["producer"],
        platform=raw["platform"],
        source=Source(**raw["source"]),
        scenarios=[Scenario(**item) for item in raw["scenarios"]],
    )
    if catalog.schemaVersion != 1 or catalog.producer != "caic" or catalog.platform != "web":
        raise ValueError("expected a version 1 caic web screenshot catalog")
    if not re.fullmatch(r"[0-9a-f]{40}", catalog.source.revision):
        raise ValueError("catalog source revision must be a Git SHA")
    if not re.fullmatch(r"[0-9a-f]{64}", catalog.source.inputsSha256):
        raise ValueError("catalog must include a capture-input SHA-256")
    files: set[str] = set()
    for item in catalog.scenarios:
        path = PurePosixPath(item.file)
        if (
            path.is_absolute()
            or ".." in path.parts
            or len(path.parts) != 2
            or path.parts[0] not in {"desktop", "mobile"}
        ):
            raise ValueError(f"invalid screenshot path: {item.file}")
        if path.suffix not in {".avif", ".webp"}:
            raise ValueError(f"expected a WebP still or AVIF animation: {item.file}")
        if item.file in files:
            raise ValueError(f"duplicate catalog scenario: {item.file}")
        files.add(item.file)
        if (
            item.width <= 0
            or item.height <= 0
            or not re.fullmatch(r"[0-9a-f]{64}", item.sha256)
            or not item.description
        ):
            raise ValueError(f"invalid screenshot metadata: {item.file}")
    return catalog


def referenced_files() -> set[str]:
    """Use page references as the curated catalog's single source of truth."""
    result: set[str] = set()
    paths = [*ROOT.glob("*.md"), *ROOT.glob("caic/*.md"), *ROOT.glob("md/*.md"), *ROOT.glob("public/*.html")]
    pattern = re.compile(re.escape(PREFIX) + r'([^\s"<>\)]+\.webp)')
    for path in paths:
        result.update(pattern.findall(read_text(path)))
    if not result:
        raise ValueError("site does not reference any caic screenshots")
    return result


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dimensions(path: Path) -> tuple[int, int]:
    """Read WebP image geometry from its bounded format header."""
    with path.open("rb") as stream:
        header = stream.read(32)
    if len(header) < 30 or header[:4] != b"RIFF" or header[8:12] != b"WEBP":
        raise ValueError(f"invalid WebP header: {path.name}")
    kind = header[12:16]
    if kind == b"VP8X":
        return int.from_bytes(header[24:27], "little") + 1, int.from_bytes(header[27:30], "little") + 1
    if kind == b"VP8 " and header[23:26] == b"\x9d\x01\x2a":
        w, h = struct.unpack_from("<HH", header, 26)
        return w & 0x3FFF, h & 0x3FFF
    if kind == b"VP8L" and header[20] == 0x2F:
        value = int.from_bytes(header[21:25], "little")
        return (value & 0x3FFF) + 1, ((value >> 14) & 0x3FFF) + 1
    raise ValueError(f"unsupported WebP geometry header: {path.name}")


def validate(directory: Path, scenarios: list[Scenario]) -> None:
    for item in scenarios:
        path = directory / item.file
        if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"screenshot missing or symlinked: {item.file}")
        if path.resolve().parent.parent != directory.resolve():
            raise ValueError(f"screenshot resolves outside catalog: {item.file}")
        if digest(path) != item.sha256 or dimensions(path) != (item.width, item.height):
            raise ValueError(f"screenshot content does not match catalog: {item.file}")


def validate_managed_path(path: Path) -> None:
    """Reject symlinks and escapes in every owned publication path ancestor."""
    if not path.is_relative_to(ROOT):
        raise ValueError("screenshot publication path is outside the repository")
    current = path
    while current != ROOT:
        if current.is_symlink():
            raise ValueError("refusing a symlinked screenshot publication path")
        current = current.parent
    if not path.resolve().is_relative_to(ROOT):
        raise ValueError("screenshot publication path resolves outside the repository")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check committed assets without a source checkout")
    parser.add_argument("--source", type=Path, help="caic frontend catalog directory (default: sibling caic checkout)")
    args = parser.parse_args()
    if args.check and args.source:
        parser.error("--check cannot be combined with --source")
    if args.check:
        return process_catalog(True, None)
    # POSIX advisory locking serializes refreshes without writing during --check.
    try:
        validate_managed_path(LOCK)
        with LOCK.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            return process_catalog(False, args.source)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


def process_catalog(check: bool, source: Path | None) -> int:
    started = time.perf_counter()
    directory = DEST if check else source or ROOT.parent / "caic/e2e/screenshots/frontend"
    try:
        validate_managed_path(DEST)
        validate_managed_path(BACKUP)
        if BACKUP.exists() and check:
            raise ValueError("interrupted publication has a recovery catalog; run screenshots:import")
        if BACKUP.exists():
            if not DEST.exists():
                BACKUP.rename(DEST)
            else:
                # Resolve a completed publication before consulting the producer;
                # standalone validity must not depend on an available source repo.
                published = read_catalog(DEST)
                validate(DEST, published.scenarios)
                shutil.rmtree(BACKUP)
        catalog = read_catalog(directory)
        required = referenced_files()
        available = {item.file for item in catalog.scenarios}
        if missing := required - available:
            raise ValueError(f"catalog is missing referenced screenshots: {', '.join(sorted(missing))}")
        selected = sorted((item for item in catalog.scenarios if item.file in required), key=lambda item: item.file)
        validate(directory, selected)
        if check:
            actual = {path.relative_to(DEST).as_posix() for path in DEST.rglob("*.webp")}
            if actual != required or available != required:
                raise ValueError("committed catalog contains unused or uncatalogued screenshots; import again")
        else:
            DEST.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=".screenshots-stage-", dir=ROOT) as temporary:
                stage = Path(temporary) / "frontend"
                stage.mkdir()
                for item in selected:
                    target = stage / item.file
                    target.parent.mkdir(exist_ok=True)
                    shutil.copyfile(directory / item.file, target)
                subset = Catalog(catalog.schemaVersion, catalog.producer, catalog.platform, catalog.source, selected)
                (stage / "manifest.json").write_text(json.dumps(asdict(subset), indent=2) + "\n")
                validate(stage, selected)
                try:
                    if DEST.exists():
                        DEST.rename(BACKUP)
                    stage.rename(DEST)
                except BaseException:
                    # KeyboardInterrupt must restore too. Forced termination leaves a
                    # persistent backup for the next import, outside temporary cleanup.
                    if BACKUP.exists() and not DEST.exists():
                        BACKUP.rename(DEST)
                    raise
                if BACKUP.exists():
                    shutil.rmtree(BACKUP)
        action = "Checked" if check else "Imported"
        print(
            f"{action} {len(selected)} screenshots from {catalog.source.revision[:12]} "
            f"in {time.perf_counter() - started:.3f}s"
        )
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
