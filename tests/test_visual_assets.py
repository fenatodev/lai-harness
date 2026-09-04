from __future__ import annotations

import json
import re
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "local-agent"
MANIFEST = ROOT / "docs" / "assets" / "visual-assets.json"


class VisualAssetsTest(unittest.TestCase):
    def test_visual_assets_match_current_version_and_are_readme_linked(self):
        source = SOURCE.read_text(encoding="utf-8")
        match = re.search(r'^VERSION = "([^"]+)"$', source, re.MULTILINE)
        self.assertIsNotNone(match)
        version = match.group(1)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["reviewed_for_version"], version)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for item in manifest["assets"]:
            path = ROOT / "docs" / "assets" / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            self.assertIn(f"docs/assets/{item['path']}", readme)

    def test_visual_assets_are_valid_large_pngs(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for item in manifest["assets"]:
            path = ROOT / "docs" / "assets" / item["path"]
            with path.open("rb") as handle:
                signature = handle.read(8)
                self.assertEqual(signature, b"\x89PNG\r\n\x1a\n")
                length = struct.unpack(">I", handle.read(4))[0]
                self.assertEqual(handle.read(4), b"IHDR")
                self.assertEqual(length, 13)
                width, height = struct.unpack(">II", handle.read(8))
            self.assertGreaterEqual(width, 1200)
            self.assertGreaterEqual(height, 675)


if __name__ == "__main__":
    unittest.main()
