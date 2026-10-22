#!/usr/bin/env python3
"""Import referenced caic screenshots with recoverable publication and WebP validation."""

import argparse
import fcntl
import re
import shutil
import struct
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "public/screenshots/frontend"
BACKUP = ROOT / ".screenshots-previous"
LOCK = ROOT / ".screenshots-import.lock"
PREFIX = "/screenshots/frontend/"
MAX_TEXT_BYTES = 1024 * 1024


def read_text(path: Path) -> str:
    """Bound page sources to one MiB before decoding."""
    with path.open("rb") as stream:
        content = stream.read(MAX_TEXT_BYTES + 1)
    if len(content) > MAX_TEXT_BYTES:
        raise ValueError(f"text input exceeds one MiB: {path.name}")
    return content.decode("utf-8")


def validate_reference(name: str) -> str:
    """Reject references that escape a managed desktop or mobile image."""
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or ".." in path.parts
        or len(path.parts) != 2
        or path.parts[0] not in {"desktop", "mobile"}
        or path.suffix != ".webp"
        or "\\" in name
    ):
        raise ValueError(f"invalid screenshot path: {name}")
    return name


def referenced_files() -> set[str]:
    """Use page references as the curated set of screenshots."""
    result: set[str] = set()
    paths = [*ROOT.glob("*.md"), *ROOT.glob("caic/*.md"), *ROOT.glob("md/*.md"), *ROOT.glob("public/*.html")]
    pattern = re.compile(re.escape(PREFIX) + r'([^\s"<>\)]+\.webp)')
    for path in paths:
        result.update(validate_reference(name) for name in pattern.findall(read_text(path)))
    if not result:
        raise ValueError("site does not reference any caic screenshots")
    return result


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


def validate(directory: Path, files: set[str]) -> None:
    """Verify that every named image is a real, nonempty WebP inside the directory."""
    resolved = directory.resolve()
    for name in sorted(files):
        validate_reference(name)
        path = directory / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"screenshot missing or symlinked: {name}")
        if path.resolve().parent.parent != resolved:
            raise ValueError(f"screenshot resolves outside its directory: {name}")
        width, height = dimensions(path)
        if width <= 0 or height <= 0:
            raise ValueError(f"screenshot has invalid dimensions: {name}")


def directory_files(directory: Path) -> set[str]:
    """Return every file in a directory, rejecting symlinks."""
    result: set[str] = set()
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symlinked screenshot: {path.relative_to(directory).as_posix()}")
        if path.is_file():
            result.add(path.relative_to(directory).as_posix())
    return result


def validate_published(directory: Path) -> None:
    """Verify that a published directory contains only valid WebP images."""
    files = directory_files(directory)
    if not files:
        raise ValueError("published screenshot directory is empty")
    validate(directory, files)


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
    parser.add_argument("--source", type=Path, help="caic frontend screenshot directory (default: sibling checkout)")
    args = parser.parse_args()
    if args.check and args.source:
        parser.error("--check cannot be combined with --source")
    if args.check:
        return process_images(True, None)
    # POSIX advisory locking serializes refreshes without writing during --check.
    try:
        validate_managed_path(LOCK)
        with LOCK.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            return process_images(False, args.source)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


def process_images(check: bool, source: Path | None) -> int:
    started = time.perf_counter()
    directory = DEST if check else source or ROOT.parent / "caic/e2e/screenshots/frontend"
    try:
        validate_managed_path(DEST)
        validate_managed_path(BACKUP)
        if BACKUP.exists() and check:
            raise ValueError("interrupted publication has a recovery copy; run screenshots:import")
        if BACKUP.exists():
            if not DEST.exists():
                BACKUP.rename(DEST)
            else:
                # Resolve a completed publication before consulting the producer;
                # standalone validity must not depend on an available source repo.
                validate_published(DEST)
                shutil.rmtree(BACKUP)
        required = referenced_files()
        validate(directory, required)
        if check:
            actual = directory_files(DEST)
            if actual != required:
                unused = sorted(actual - required)
                missing = sorted(required - actual)
                details = []
                if unused:
                    details.append(f"unused: {', '.join(unused)}")
                if missing:
                    details.append(f"missing: {', '.join(missing)}")
                raise ValueError(f"committed screenshots do not match page references ({'; '.join(details)})")
        else:
            DEST.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=".screenshots-stage-", dir=ROOT) as temporary:
                stage = Path(temporary) / "frontend"
                stage.mkdir()
                for name in sorted(required):
                    target = stage / name
                    target.parent.mkdir(exist_ok=True)
                    shutil.copyfile(directory / name, target)
                validate(stage, required)
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
        print(f"{action} {len(required)} screenshots in {time.perf_counter() - started:.3f}s")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
