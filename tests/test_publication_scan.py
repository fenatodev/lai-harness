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

    def test_grep_fallback_rejects_private_paths_and_known_local_ips(self):
        linux_home = "/" + "/".join(["home", "fenato", "synthetic-secret-path"])
        wsl_user = "/" + "/".join(["mnt", "c", "Users", "someone", "project"])
        windows_user = "C:" + "\\".join(["", "Users", "someone", "project"])
        wsl_nat = ".".join(["172", "29", "193", "62"])
        tailnet = ".".join(["100", "107", "179", "6"])
        lan = ".".join(["192", "168", "15", "4"])
        cases = (
            ("linux-home", linux_home + "\n", "personal Linux home path"),
            ("wsl-user", wsl_user + "\n", "personal WSL Windows-user path"),
            ("windows-user", windows_user + "\n", "personal Windows user path"),
            ("wsl-nat", wsl_nat + "\n", "local WSL NAT IP"),
            ("tailnet", tailnet + "\n", "known local tailnet IP"),
            ("lan", lan + "\n", "known local LAN IP"),
        )
        for name, content, label in cases:
            with self.subTest(name=name):
                tmp, root, scanner, bin_dir = self.make_sandbox()
                self.addCleanup(tmp.cleanup)

                (root / "leak.txt").write_text(content, encoding="utf-8")

                result = self.run_scan(root, scanner, bin_dir)

                self.assertEqual(result.returncode, 1)
                self.assertIn(label, result.stderr)
                self.assertIn("./leak.txt:1:", result.stdout)

    def test_gitignore_excludes_private_runtime_and_build_artifacts(self):
        ignored_paths = (
            ".pytest_cache/cache",
            ".mypy_cache/cache",
            ".ruff_cache/cache",
            ".venv/pyvenv.cfg",
            ".env",
            ".env.local",
            ".secrets/model-api-key",
            "dist/lai-harness.vsix",
            "build/temp",
            "state/session.json",
            "metrics/events.jsonl",
            "audit/events.jsonl",
            "events.jsonl",
            "current-context.json",
            "api-key",
            "private.key",
            "debug.log",
            "models/example.gguf",
            "runtime.sqlite",
            "runtime.sqlite3",
            "htmlcov/index.html",
        )
        result = subprocess.run(
            ["git", "check-ignore", "--stdin"],
            cwd=ROOT,
            input="\n".join(ignored_paths) + "\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(result.stdout.splitlines()), set(ignored_paths))

        env_example = subprocess.run(
            ["git", "check-ignore", ".env.example"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        self.assertNotEqual(env_example.returncode, 0)


if __name__ == "__main__":
    unittest.main()
