from __future__ import annotations

import json
import re
import struct
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "local-agent"
MANIFEST = ROOT / "docs" / "assets" / "visual-assets.json"
DOCS_ROOT = ROOT / "docs" / "assets"


class VisualAssetsTest(unittest.TestCase):
    def _manifest(self):
        return json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_visual_assets_match_current_version_and_are_declared(self):
        source = SOURCE.read_text(encoding="utf-8")
        match = re.search(r'^VERSION = "([^"]+)"$', source, re.MULTILINE)
        self.assertIsNotNone(match)
        version = match.group(1)
        manifest = self._manifest()
        self.assertEqual(manifest["reviewed_for_version"], version)
        self.assertEqual(
            manifest["audit_scope"],
            "all tracked PNG and SVG documentation assets under docs/assets",
        )

        declared = {item["path"] for item in manifest["assets"]}
        declared_sources = {item["source"] for item in manifest["assets"] if item.get("source")}
        tracked = subprocess.check_output(
            [
                "git",
                "ls-files",
                "docs/assets/*.png",
                "docs/assets/*.svg",
                "docs/assets/diagrams/*.svg",
                "docs/assets/screenshots/*.svg",
            ],
            cwd=ROOT,
            text=True,
        ).splitlines()
        tracked_rel = {str((ROOT / path).relative_to(DOCS_ROOT)) for path in tracked}
        self.assertEqual(declared | declared_sources, tracked_rel)

    def test_visual_assets_have_valid_format_and_references(self):
        searchable_docs = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [
                ROOT / "README.md",
                ROOT / "README.pt-BR.md",
                *sorted((ROOT / "docs").glob("*.md")),
            ]
        )
        for item in self._manifest()["assets"]:
            rel_path = item["path"]
            path = DOCS_ROOT / rel_path
            self.assertTrue(path.is_file(), rel_path)
            self.assertNotEqual(item.get("purpose"), "", rel_path)
            for reference in item.get("references", []):
                self.assertTrue((ROOT / reference).is_file(), reference)
            if item.get("source"):
                source_path = DOCS_ROOT / item["source"]
                self.assertTrue(source_path.is_file(), item["source"])
                self.assertIn("<svg", source_path.read_text(encoding="utf-8")[:500])

            if path.suffix.lower() == ".png":
                with path.open("rb") as handle:
                    signature = handle.read(8)
                    self.assertEqual(signature, b"\x89PNG\r\n\x1a\n")
                    length = struct.unpack(">I", handle.read(4))[0]
                    self.assertEqual(handle.read(4), b"IHDR")
                    self.assertEqual(length, 13)
                    width, height = struct.unpack(">II", handle.read(8))
                self.assertGreaterEqual(width, 1200, rel_path)
                self.assertGreaterEqual(height, 675, rel_path)
            else:
                self.assertEqual(path.suffix.lower(), ".svg", rel_path)
                self.assertIn("<svg", path.read_text(encoding="utf-8")[:500])

            self.assertIn(rel_path, searchable_docs, rel_path)

    def test_visual_assets_do_not_advertise_obsolete_current_capabilities(self):
        forbidden_current_claims = [
            "beta.15",
            "GitHub Pre-release",
            "Version and publish",
            "Secure, automated, and auditable release flow",
        ]
        audited_svg_paths = set()
        for item in self._manifest()["assets"]:
            audited_svg_paths.add(item["path"])
            if item.get("source"):
                audited_svg_paths.add(item["source"])
        for rel_path in sorted(audited_svg_paths):
            path = DOCS_ROOT / rel_path
            if path.suffix.lower() != ".svg":
                continue
            text = path.read_text(encoding="utf-8")
            for claim in forbidden_current_claims:
                self.assertNotIn(claim, text, f"{claim!r} in {rel_path}")

    def test_readiness_screenshot_is_sanitized_ready_fixture(self):
        source = (DOCS_ROOT / "screenshots" / "lai-readiness.svg").read_text(encoding="utf-8")
        self.assertIn('\"detail\": \"[clean]\"', source)
        self.assertIn('\"overall\": \"ready\"', source)
        self.assertIn("unauthenticated=401 authenticated=200", source)
        self.assertNotIn("AGENTS.md", source)
        self.assertNotIn("ROADMAP.md", source)


if __name__ == "__main__":
    unittest.main()
