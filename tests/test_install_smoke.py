import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from fake_llama_server import FakeLlamaServer


REPO = Path(__file__).parents[1]


class IsolatedInstallSmokeTest(unittest.TestCase):
    def test_install_doctor_sample_repo_and_deterministic_commands(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bin_dir = root / "bin"
            data_dir = root / "data"
            key_file = root / "key"
            sample_repo = root / "sample-repo"
            key_file.write_text("synthetic-test-key")
            sample_repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=sample_repo, check=True)

            install_env = {
                **os.environ,
                "LAI_BIN_DIR": str(bin_dir),
                "LAI_DATA_DIR": str(data_dir),
            }
            install = subprocess.run(
                [str(REPO / "scripts" / "install-local.sh")],
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Installed lai harness", install.stdout)
            self.assertTrue((bin_dir / "lai").is_file())
            self.assertTrue((bin_dir / "lai-server-start").is_file())
            self.assertTrue((bin_dir / "lai-server-stop").is_file())
            self.assertTrue((bin_dir / "lai-server-restart").is_file())
            self.assertTrue((data_dir / "skills" / "implement.txt").is_file())
            self.assertTrue((data_dir / "skills" / "implement" / "SKILL.md").is_file())
            self.assertTrue((data_dir / "skills" / "diagnose" / "SKILL.md").is_file())
            self.assertTrue((data_dir / "skills" / "ci-fix" / "SKILL.md").is_file())
            self.assertTrue((data_dir / "skills" / "release" / "SKILL.md").is_file())
            restart_source = (bin_dir / "lai-server-restart").read_text()
            self.assertIn("lai-server-stop", restart_source)
            self.assertIn("lai-server-start", restart_source)

            version = subprocess.run(
                [str(bin_dir / "lai"), "version"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("lai harness", version.stdout)

            status = subprocess.run(
                [str(bin_dir / "lai"), "status"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn(str(sample_repo), status.stdout)
            self.assertIn("## Git status", status.stdout)

            workspace_status = subprocess.run(
                [str(bin_dir / "lai"), "workspace", "status", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            workspace_payload = json.loads(workspace_status.stdout)
            self.assertEqual(workspace_payload["version"], "0.4.0-beta.5")
            self.assertEqual(workspace_payload["repository"], str(sample_repo.resolve()))
            self.assertIn("base_dir", workspace_payload)

            model_plan = subprocess.run(
                [str(bin_dir / "lai"), "model", "plan"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("# lai model evaluation", model_plan.stdout)
            self.assertIn("does not call, start, or download a model", model_plan.stdout)

            semantics = subprocess.run(
                [str(bin_dir / "lai"), "semantics"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("# lai code semantics", semantics.stdout)
            self.assertIn("policy-gateway", semantics.stdout)

            runs = subprocess.run(
                [str(bin_dir / "lai"), "runs"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("# lai run history", runs.stdout)
            self.assertIn("Recorded runs: 0", runs.stdout)

            readiness = subprocess.run(
                [str(bin_dir / "lai"), "readiness", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            readiness_payload = json.loads(readiness.stdout)
            self.assertEqual(readiness_payload["version"], "0.4.0-beta.5")
            modes = {item["mode"] for item in readiness_payload["skills"]}
            self.assertTrue({"diagnose", "ci-fix", "release"}.issubset(modes))

            release_check = subprocess.run(
                [str(bin_dir / "lai"), "release-check", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            release_payload = json.loads(release_check.stdout)
            self.assertEqual(release_payload["version"], "0.4.0-beta.5")
            self.assertIn("release_safety", {item["name"] for item in release_payload["checks"]})

            release_pack = subprocess.run(
                [
                    str(bin_dir / "lai"),
                    "release-pack",
                    "--target",
                    "0.4.0-beta.5",
                    "--out",
                    str(root / "release-pack"),
                    "--json",
                ],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            release_pack_payload = json.loads(release_pack.stdout)
            self.assertEqual(release_pack_payload["version"], "0.4.0-beta.5")
            self.assertTrue(Path(release_pack_payload["files"]["release_body"]).is_file())

            no_last = subprocess.run(
                [str(bin_dir / "lai"), "run", "last"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, no_last.returncode)
            self.assertIn("No runs recorded", no_last.stderr)

            no_export = subprocess.run(
                [str(bin_dir / "lai"), "run", "export", "--last"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, no_export.returncode)
            self.assertIn("No runs recorded", no_export.stderr)

            for mode_command, expected in (
                ("diagnose", "diagnose-alias-ok"),
                ("ci-fix", "ci-fix-alias-ok"),
                ("release", "release-alias-ok"),
            ):
                alias = subprocess.run(
                    [str(bin_dir / "lai"), mode_command, f"respond only: {expected}"],
                    cwd=sample_repo,
                    env=install_env,
                    text=True,
                    capture_output=True,
                    check=True,
                )
                self.assertEqual(alias.stdout.strip(), expected)

            with FakeLlamaServer() as server:
                runtime_env = {
                    **install_env,
                    "LAI_HOST": server.host,
                    "LAI_PORT": str(server.port),
                    "LAI_API_KEY_FILE": str(key_file),
                }
                doctor = subprocess.run(
                    [str(bin_dir / "lai"), "doctor"],
                    cwd=sample_repo,
                    env=runtime_env,
                    text=True,
                    capture_output=True,
                    check=True,
                )
            self.assertIn("Authentication: OK", doctor.stdout)


    def test_server_start_requires_authentication_enforcement(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            key_file = root / "key"
            key_file.write_text("synthetic-test-key")

            base_env = {
                **os.environ,
                "LAI_API_KEY_FILE": str(key_file),
                "LAI_WINDOWS_LAUNCHER": "/tmp/synthetic-start-secure.ps1",
            }

            with FakeLlamaServer() as secure_server:
                secure = subprocess.run(
                    [str(REPO / "scripts" / "ministral-start")],
                    env={
                        **base_env,
                        "LAI_HOST": secure_server.host,
                        "LAI_PORT": str(secure_server.port),
                    },
                    text=True,
                    capture_output=True,
                )

            self.assertEqual(secure.returncode, 0)
            self.assertIn(
                "already running securely",
                secure.stdout,
            )

            with FakeLlamaServer(require_auth=False) as insecure_server:
                insecure = subprocess.run(
                    [str(REPO / "scripts" / "ministral-start")],
                    env={
                        **base_env,
                        "LAI_HOST": insecure_server.host,
                        "LAI_PORT": str(insecure_server.port),
                    },
                    text=True,
                    capture_output=True,
                )

            self.assertEqual(insecure.returncode, 1)
            self.assertIn(
                "Refusing insecure LAI model server",
                insecure.stderr,
            )


if __name__ == "__main__":
    unittest.main()
