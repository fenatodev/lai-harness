import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "check-publication.sh"


class PublicationScanTest(unittest.TestCase):
    def make_sandbox(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)

        scripts = root / "scripts"
        scripts.mkdir()

        scanner = scripts / "check-publication.sh"
        shutil.copy2(SOURCE, scanner)

        bin_dir = root / "bin"
        bin_dir.mkdir()

        for name in ("bash", "grep", "find", "dirname"):
            target = shutil.which(name)
            self.assertIsNotNone(target, name)
            (bin_dir / name).symlink_to(target)

        return tmp, root, scanner, bin_dir

    def run_scan(self, root, scanner, bin_dir):
        env = os.environ.copy()
        env["PATH"] = str(bin_dir)
        return subprocess.run(
            [str(scanner)],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_grep_fallback_passes_clean_repository(self):
        tmp, root, scanner, bin_dir = self.make_sandbox()
        self.addCleanup(tmp.cleanup)

        result = self.run_scan(root, scanner, bin_dir)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Publication scan passed", result.stdout)
        self.assertNotIn("rg: command not found", result.stderr)

    def test_grep_fallback_rejects_forbidden_path(self):
        tmp, root, scanner, bin_dir = self.make_sandbox()
        self.addCleanup(tmp.cleanup)

        forbidden_path = "/" + "/".join(
            ["home", "fenato", "synthetic-secret-path"]
        )
        (root / "leak.txt").write_text(forbidden_path + "\n")

        result = self.run_scan(root, scanner, bin_dir)

        self.assertEqual(result.returncode, 1)
        self.assertIn("personal Linux path", result.stderr)
        self.assertIn("./leak.txt:1:", result.stdout)


if __name__ == "__main__":
    unittest.main()
