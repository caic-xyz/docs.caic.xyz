#!/usr/bin/env python3
"""Process-level coverage for screenshot import integrity, curation, and failed-import preservation."""

import base64
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# A complete one-pixel lossless WebP fixture, independent of the importer.
PIXEL = base64.b64decode("UklGRiIAAABXRUJQVlA4TBUAAAAvAAAAAAfQ//73v/+BiOh/AAA=")


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.site = self.root / "site"
        self.source = self.root / "captures"
        (self.site / "scripts").mkdir(parents=True)
        (self.site / "public").mkdir()
        (self.source / "desktop").mkdir(parents=True)
        self.script = self.site / "scripts/import-screenshots.py"
        shutil.copyfile(Path(__file__).with_name("import-screenshots.py"), self.script)
        (self.site / "public/index.html").write_text('<img src="/screenshots/frontend/desktop/example.webp">')
        (self.source / "desktop/example.webp").write_bytes(PIXEL)
        self.manifest = {
            "schemaVersion": 1,
            "producer": "caic",
            "platform": "web",
            "source": {"revision": "0" * 40, "inputsSha256": "1" * 64},
            "scenarios": [
                {
                    "name": "example",
                    "file": "desktop/example.webp",
                    "width": 1,
                    "height": 1,
                    "sha256": hashlib.sha256(PIXEL).hexdigest(),
                    "description": "A one-pixel test fixture",
                }
            ],
        }
        self.write_manifest()

    def write_manifest(self):
        (self.source / "manifest.json").write_text(json.dumps(self.manifest))

    def run_import(self, *arguments):
        return subprocess.run(
            [sys.executable, str(self.script), *arguments], capture_output=True, text=True, check=False
        )

    def import_successfully(self):
        result = self.run_import("--source", str(self.source))
        self.assertEqual(result.returncode, 0, result.stderr)

    def interrupt_publication(self, exit_code):
        # Inject interruption at the directory publication boundary in an isolated
        # process, without adding a production testing seam.
        program = """
import os
import runpy
import sys
from pathlib import Path
original = Path.rename
termination = sys.argv[3]
def rename(path, target):
    if path.name == "frontend" and path.parent.name.startswith(".screenshots-stage-"):
        if termination == "published":
            original(path, target)
            os._exit(92)
        if termination == "forced":
            os._exit(91)
        raise KeyboardInterrupt
    return original(path, target)
Path.rename = rename
script, source = sys.argv[1:3]
sys.argv = [script, "--source", source]
runpy.run_path(script, run_name="__main__")
"""
        return subprocess.run(
            [sys.executable, "-c", program, str(self.script), str(self.source), exit_code],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_keyboard_interrupt_restores_previous_publish(self):
        self.import_successfully()
        result = self.interrupt_publication("keyboard")
        self.assertNotEqual(result.returncode, 0)
        check = self.run_import("--check")
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertFalse((self.site / ".screenshots-previous").exists())

    def test_forced_termination_retains_recoverable_catalog(self):
        self.import_successfully()
        result = self.interrupt_publication("forced")
        self.assertEqual(result.returncode, 91)
        self.assertTrue((self.site / ".screenshots-previous").is_dir())
        self.assertNotEqual(self.run_import("--check").returncode, 0)
        self.assertTrue((self.site / ".screenshots-previous").is_dir())
        # Recovery precedes source validation, so even a failed new refresh restores
        # the existing publish that was retained outside temporary staging.
        (self.source / "desktop/example.webp").write_bytes(b"corrupt")
        self.assertNotEqual(self.run_import("--source", str(self.source)).returncode, 0)
        check = self.run_import("--check")
        self.assertEqual(check.returncode, 0, check.stderr)

    def test_completed_publish_recovers_without_producer(self):
        self.import_successfully()
        result = self.interrupt_publication("published")
        self.assertEqual(result.returncode, 92)
        self.assertTrue((self.site / ".screenshots-previous").is_dir())
        self.assertTrue((self.site / "public/screenshots/frontend").is_dir())
        shutil.rmtree(self.source)
        # Source failure is still reported, but cleanup restores standalone builds.
        self.assertNotEqual(self.run_import("--source", str(self.source)).returncode, 0)
        self.assertFalse((self.site / ".screenshots-previous").exists())
        result = self.run_import("--check")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_import_and_standalone_check(self):
        self.import_successfully()
        shutil.rmtree(self.source)
        result = self.run_import("--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        published = self.site / "public/screenshots/frontend/desktop/example.webp"
        self.assertEqual(published.read_bytes(), PIXEL)

    def test_corrupted_source_preserves_previous_catalog(self):
        self.import_successfully()
        catalog = self.site / "public/screenshots/frontend/manifest.json"
        previous = catalog.read_bytes()
        (self.source / "desktop/example.webp").write_bytes(b"corrupt")
        result = self.run_import("--source", str(self.source))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match catalog", result.stderr)
        self.assertEqual(catalog.read_bytes(), previous)

    def test_oversized_catalog_preserves_previous_publish(self):
        self.import_successfully()
        published = self.site / "public/screenshots/frontend/manifest.json"
        previous = published.read_bytes()
        (self.source / "manifest.json").write_bytes(b" " * (1024 * 1024 + 1))
        result = self.run_import("--source", str(self.source))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exceeds one MiB", result.stderr)
        self.assertEqual(published.read_bytes(), previous)

    def test_wrong_dimensions_rejected(self):
        self.manifest["scenarios"][0]["width"] = 20
        self.write_manifest()
        result = self.run_import("--source", str(self.source))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.site / "public/screenshots/frontend").exists())

    def test_path_escape_rejected(self):
        self.manifest["scenarios"][0]["file"] = "desktop/../../outside.webp"
        self.write_manifest()
        result = self.run_import("--source", str(self.source))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid screenshot path", result.stderr)

    def test_new_reference_requires_new_catalog(self):
        self.import_successfully()
        (self.site / "guide.md").write_text('<img src="/screenshots/frontend/mobile/missing.webp">')
        result = self.run_import("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing referenced screenshots", result.stderr)

    def test_symlinked_public_ancestor_cannot_replace_outside_assets(self):
        outside = self.root / "outside-public"
        (self.site / "public").rename(outside)
        (self.site / "public").symlink_to(outside, target_is_directory=True)
        preserved = outside / "screenshots/frontend/keep.txt"
        preserved.parent.mkdir(parents=True)
        preserved.write_text("Preserve outside assets")
        result = self.run_import("--source", str(self.source))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked", result.stderr)
        self.assertEqual(preserved.read_text(), "Preserve outside assets")
        self.assertFalse((self.site / ".screenshots-previous").exists())

    def test_symlinked_lock_cannot_create_an_outside_file(self):
        outside = self.root / "outside.lock"
        (self.site / ".screenshots-import.lock").symlink_to(outside)
        result = self.run_import("--source", str(self.source))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked", result.stderr)
        self.assertFalse(outside.exists())
        self.assertFalse((self.site / "public/screenshots/frontend").exists())

    def test_symlinked_capture_rejected(self):
        picture = self.source / "desktop/example.webp"
        picture.unlink()
        outside = self.root / "outside.webp"
        outside.write_bytes(PIXEL)
        picture.symlink_to(outside)
        result = self.run_import("--source", str(self.source))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked", result.stderr)


if __name__ == "__main__":
    unittest.main()
