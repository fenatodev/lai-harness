import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

EXPECTED = {
    "actions/checkout": ("3d3c42e5aac5ba805825da76410c181273ba90b1", "v7.0.1"),
    "actions/setup-python": ("5fda3b95a4ea91299a34e894583c3862153e4b97", "v7.0.0"),
    "actions/setup-node": ("820762786026740c76f36085b0efc47a31fe5020", "v7.0.0"),
}


class GitHubActionsHardeningTest(unittest.TestCase):
    def test_official_github_actions_are_sha_pinned(self):
        seen = set()
        pattern = re.compile(
            r"uses:\s+(actions/[\w-]+)@([0-9a-f]{40})(?:\s+#\s+(v[^\s]+))?"
        )
        for workflow in WORKFLOWS.glob("*.yml"):
            for line in workflow.read_text().splitlines():
                if "uses: actions/" not in line:
                    continue
                match = pattern.search(line)
                self.assertIsNotNone(
                    match,
                    f"official action is not pinned to a full SHA: {workflow}: {line}",
                )
                assert match is not None
                name, sha, version = match.groups()
                self.assertIn(name, EXPECTED, f"unreviewed official action dependency: {name}")
                self.assertEqual((sha, version), EXPECTED[name])
                seen.add(name)
        self.assertEqual(seen, set(EXPECTED))

    def test_publication_uses_node24_without_package_cache(self):
        ci = (WORKFLOWS / "ci.yml").read_text()
        self.assertIn('node-version: "24"', ci)
        self.assertIn("package-manager-cache: false", ci)
        self.assertNotIn('node-version: "20"', ci)

    def test_dependabot_tracks_github_actions(self):
        config = (ROOT / ".github" / "dependabot.yml").read_text()
        self.assertIn('package-ecosystem: "github-actions"', config)
        self.assertIn('directory: "/"', config)
        self.assertIn('interval: "weekly"', config)


if __name__ == "__main__":
    unittest.main()
