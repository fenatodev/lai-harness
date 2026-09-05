import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request

from fake_llama_server import FakeLlamaServer


REPO = Path(__file__).parents[1]


class IsolatedInstallSmokeTest(unittest.TestCase):
    def test_install_doctor_sample_repo_and_deterministic_commands(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bin_dir = root / "bin"
            data_dir = root / "data"
            config_dir = root / "config"
            key_file = root / "key"
            sample_repo = root / "sample-repo"
            key_file.write_text("synthetic-test-key")
            sample_repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=sample_repo, check=True)

            install_env = {
                **os.environ,
                "LAI_BIN_DIR": str(bin_dir),
                "LAI_DATA_DIR": str(data_dir),
                "LAI_CONFIG_DIR": str(config_dir),
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
            self.assertEqual(workspace_payload["version"], "0.4.0-beta.17")
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

            policy_check = subprocess.run(
                [
                    str(bin_dir / "lai"),
                    "policy-check",
                    "--tool",
                    "bash",
                    "--command",
                    "git status --short",
                    "--json",
                ],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            policy_payload = json.loads(policy_check.stdout)
            self.assertEqual(policy_payload["decision"], "ALLOW")
            self.assertFalse(policy_payload["executed"])

            control_token = subprocess.run(
                [str(bin_dir / "lai"), "control-token", "init", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            control_token_payload = json.loads(control_token.stdout)
            control_token_path = Path(control_token_payload["path"])
            self.assertTrue(control_token_path.is_file())
            self.assertEqual(control_token_path.stat().st_mode & 0o777, 0o600)
            self.assertFalse(control_token_payload["secret_printed"])
            control_secret = control_token_path.read_text(encoding="utf-8").strip()
            self.assertNotIn(control_secret, control_token.stdout)

            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                control_port = probe.getsockname()[1]
            with FakeLlamaServer() as llama:
                control_env = {
                    **install_env,
                    "LAI_HOST": llama.host,
                    "LAI_PORT": str(llama.port),
                    "LAI_API_KEY_FILE": str(key_file),
                }
                control_server = subprocess.Popen(
                    [str(bin_dir / "lai"), "serve", "--port", str(control_port)],
                    cwd=sample_repo,
                    env=control_env,
                    text=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                try:
                    control_payload = None
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        request = urllib.request.Request(
                            f"http://127.0.0.1:{control_port}/v1/status",
                            headers={"Authorization": f"Bearer {control_secret}"},
                        )
                        try:
                            with urllib.request.urlopen(request, timeout=1) as response:
                                control_payload = json.loads(response.read().decode("utf-8"))
                                break
                        except (urllib.error.URLError, TimeoutError):
                            time.sleep(0.05)
                    self.assertIsNotNone(control_payload, "installed lai serve did not become ready")
                    self.assertEqual(control_payload["repository"], str(sample_repo.resolve()))
                    self.assertTrue(control_payload["capabilities"]["model_execution"])
                    self.assertFalse(control_payload["capabilities"]["shell_execution"])
                    self.assertTrue(control_payload["capabilities"]["async_read_only_runs"])

                    run_request = urllib.request.Request(
                        f"http://127.0.0.1:{control_port}/v1/runs",
                        data=json.dumps({
                            "mode": "plan",
                            "task": "return a concise installed read-only plan",
                        }).encode("utf-8"),
                        method="POST",
                        headers={
                            "Authorization": f"Bearer {control_secret}",
                            "Content-Type": "application/json",
                        },
                    )
                    with urllib.request.urlopen(run_request, timeout=2) as response:
                        self.assertEqual(response.status, 202)
                        run_payload = json.loads(response.read().decode("utf-8"))
                    control_run_id = run_payload["run"]["control_run_id"]
                    deadline = time.monotonic() + 8
                    terminal = None
                    while time.monotonic() < deadline:
                        request = urllib.request.Request(
                            f"http://127.0.0.1:{control_port}/v1/runs/{control_run_id}",
                            headers={"Authorization": f"Bearer {control_secret}"},
                        )
                        with urllib.request.urlopen(request, timeout=2) as response:
                            terminal = json.loads(response.read().decode("utf-8"))["run"]
                        if terminal["status"] in {"succeeded", "failed", "cancelled"}:
                            break
                        time.sleep(0.05)
                    self.assertIsNotNone(terminal)
                    self.assertEqual(terminal["status"], "succeeded", terminal.get("stderr"))
                    self.assertIn("fake response", terminal["stdout"])
                finally:
                    control_server.terminate()
                    try:
                        control_server.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        control_server.kill()
                        control_server.wait(timeout=3)

            runs = subprocess.run(
                [str(bin_dir / "lai"), "runs"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("# lai run history", runs.stdout)
            self.assertIn("Recorded runs: 1", runs.stdout)
            self.assertIn("mode=plan", runs.stdout)

            readiness = subprocess.run(
                [str(bin_dir / "lai"), "readiness", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            readiness_payload = json.loads(readiness.stdout)
            self.assertEqual(readiness_payload["version"], "0.4.0-beta.17")
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
            self.assertEqual(release_payload["version"], "0.4.0-beta.17")
            self.assertIn("release_safety", {item["name"] for item in release_payload["checks"]})

            release_pack = subprocess.run(
                [
                    str(bin_dir / "lai"),
                    "release-pack",
                    "--target",
                    "0.4.0-beta.17",
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
            self.assertEqual(release_pack_payload["version"], "0.4.0-beta.17")
            self.assertTrue(Path(release_pack_payload["files"]["release_body"]).is_file())

            governance = subprocess.run(
                [
                    str(bin_dir / "lai"),
                    "release-governance",
                    "--target",
                    "0.4.0-beta.17",
                    "--json",
                ],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            governance_payload = json.loads(governance.stdout)
            self.assertEqual(governance_payload["version"], "0.4.0-beta.17")
            self.assertIn("manual_actions", governance_payload)

            alias_governance = subprocess.run(
                [str(bin_dir / "lai"), "governance", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            alias_governance_payload = json.loads(alias_governance.stdout)
            self.assertEqual(alias_governance_payload["version"], "0.4.0-beta.17")
            self.assertIn("github_release", {item["id"] for item in alias_governance_payload["manual_actions"]})

            project_handoff = subprocess.run(
                [
                    str(bin_dir / "lai"),
                    "project-handoff",
                    "--target",
                    "0.4.0-beta.17",
                    "--out",
                    str(root / "project-handoff"),
                    "--json",
                ],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            project_handoff_payload = json.loads(project_handoff.stdout)
            self.assertEqual(project_handoff_payload["version"], "0.4.0-beta.17")
            self.assertTrue(Path(project_handoff_payload["files"]["markdown"]).is_file())

            next_chat = subprocess.run(
                [str(bin_dir / "lai"), "next-chat", "--target", "0.4.0-beta.17", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            next_chat_payload = json.loads(next_chat.stdout)
            self.assertEqual(next_chat_payload["version"], "0.4.0-beta.17")
            self.assertIn("critical_rules", next_chat_payload)

            last_run = subprocess.run(
                [str(bin_dir / "lai"), "run", "last"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Mode: plan", last_run.stdout)
            self.assertIn("Status: completed", last_run.stdout)

            export_dir = root / "run-export"
            exported = subprocess.run(
                [
                    str(bin_dir / "lai"), "run", "export", "--last",
                    "--out", str(export_dir), "--json",
                ],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            export_payload = json.loads(exported.stdout)
            self.assertTrue(Path(export_payload["export_dir"]).is_dir())
            export_summary = json.loads(
                (Path(export_payload["export_dir"]) / "summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(export_summary["run"]["mode"], "plan")

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
