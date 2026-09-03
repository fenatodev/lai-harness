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
            self.assertIn("Installed lai/local-agent", install.stdout)
            self.assertTrue((bin_dir / "lai").is_file())
            self.assertTrue((bin_dir / "lai-server-start").is_file())
            self.assertTrue((bin_dir / "lai-server-stop").is_file())
            self.assertTrue((bin_dir / "lai-server-restart").is_file())
            self.assertTrue((data_dir / "skills" / "implement.txt").is_file())
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
            self.assertIn("lai-local-agent", version.stdout)

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


if __name__ == "__main__":
    unittest.main()
