import json
import os
import re
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
VERSION_MATCH = re.search(
    r'^VERSION = "([^"]+)"$',
    (REPO / "src" / "local-agent").read_text(encoding="utf-8"),
    re.MULTILINE,
)
if VERSION_MATCH is None:
    raise RuntimeError("cannot read canonical lai harness version")
EXPECTED_VERSION = VERSION_MATCH.group(1)


def installed_completion(content):
    return {
        "choices": [{"message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13},
    }


def installed_tool_call(call_id, name, arguments):
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [{
                    "id": call_id,
                    "type": "function",
                    "function": {"name": name, "arguments": json.dumps(arguments)},
                }],
            }
        }],
        "usage": {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13},
    }


class InstalledSequenceResponder:
    def __init__(self, responses):
        self.responses = list(responses)
        self.payloads = []

    def __call__(self, payload, requests):
        self.payloads.append(payload)
        if not self.responses:
            raise AssertionError("fake response sequence exhausted")
        response = self.responses.pop(0)
        return response(payload) if callable(response) else response


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
            self.assertTrue((bin_dir / "lai_semantics.py").is_file())
            self.assertTrue((bin_dir / "lai_config.py").is_file())
            self.assertTrue((bin_dir / "lai_specs.py").is_file())
            self.assertTrue((bin_dir / "lai_sessions.py").is_file())
            self.assertTrue((bin_dir / "lai_mcp.py").is_file())
            self.assertTrue((bin_dir / "lai_web.py").is_file())
            self.assertTrue((bin_dir / "lai-server-start").is_file())
            self.assertTrue((bin_dir / "lai-server-stop").is_file())
            self.assertTrue((bin_dir / "lai-server-restart").is_file())
            self.assertTrue((data_dir / "skills" / "implement.txt").is_file())
            self.assertTrue((data_dir / "skills" / "implement" / "SKILL.md").is_file())
            self.assertTrue((data_dir / "skills" / "diagnose" / "SKILL.md").is_file())
            self.assertTrue((data_dir / "skills" / "ci-fix" / "SKILL.md").is_file())
            self.assertTrue((data_dir / "skills" / "release" / "SKILL.md").is_file())
            self.assertTrue((data_dir / "model-eval" / "fixtures-v1.json").is_file())
            restart_source = (bin_dir / "lai-server-restart").read_text()
            self.assertIn("lai-server-stop", restart_source)
            self.assertIn("lai-server-start", restart_source)

            for command, expected in {
                "doctor": "Usage: lai doctor",
                "config": "Usage: lai config",
                "status": "Usage: lai status",
            }.items():
                with self.subTest(command=command):
                    help_result = subprocess.run(
                        [str(bin_dir / "lai"), command, "--help"],
                        cwd=sample_repo,
                        env=install_env,
                        text=True,
                        capture_output=True,
                        check=True,
                    )
                    self.assertIn(expected, help_result.stdout)
                    self.assertEqual(help_result.stderr, "")

            version = subprocess.run(
                [str(bin_dir / "lai"), "version"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("lai harness", version.stdout)

            top_help = subprocess.run(
                [str(bin_dir / "lai"), "--help"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Usage: lai <command> [options]", top_help.stdout)
            self.assertIn("web", top_help.stdout)
            self.assertEqual(top_help.stderr, "")

            web_help = subprocess.run(
                [str(bin_dir / "lai"), "web", "--help"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Usage: lai web search", web_help.stdout)
            self.assertEqual(web_help.stderr, "")

            checkpoint_help = subprocess.run(
                [str(bin_dir / "lai"), "checkpoint", "--help"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Usage: lai checkpoint", checkpoint_help.stdout)
            self.assertEqual(checkpoint_help.stderr, "")

            checkpoint_list = subprocess.run(
                [str(bin_dir / "lai"), "checkpoint", "list", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(json.loads(checkpoint_list.stdout)["checkpoint_count"], 0)

            snapshot_help = subprocess.run(
                [str(bin_dir / "lai"), "snapshot", "--help"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Usage: lai snapshot", snapshot_help.stdout)
            self.assertEqual(snapshot_help.stderr, "")

            rollback_help = subprocess.run(
                [str(bin_dir / "lai"), "rollback", "--help"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Usage: lai rollback", rollback_help.stdout)
            self.assertEqual(rollback_help.stderr, "")

            invalid_web = subprocess.run(
                [str(bin_dir / "lai"), "web", "fetch", "http://example.com/"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(invalid_web.returncode, 0)
            self.assertIn("only HTTPS URLs are allowed", invalid_web.stderr)

            config = subprocess.run(
                [str(bin_dir / "lai"), "config"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("# lai config", config.stdout)
            self.assertIn("api_key_file", config.stdout)

            gateway_contract = subprocess.run(
                [str(bin_dir / "lai"), "gateway-contract", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            gateway_payload = json.loads(gateway_contract.stdout)
            self.assertEqual(gateway_payload["schema_version"], 1)
            self.assertEqual(gateway_payload["companion"]["name"], "lai-gateway")
            self.assertIn(
                "/v1/gateway-contract",
                [route["path"] for route in gateway_payload["routes"]],
            )

            spec_status = subprocess.run(
                [str(bin_dir / "lai"), "spec"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("# lai active spec", spec_status.stdout)
            self.assertIn("Status: none", spec_status.stdout)

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
            self.assertEqual(workspace_payload["version"], EXPECTED_VERSION)
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

            mcp_status = subprocess.run(
                [str(bin_dir / "lai"), "mcp", "status", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            mcp_payload = json.loads(mcp_status.stdout)
            self.assertEqual(mcp_payload["version"], EXPECTED_VERSION)
            self.assertEqual(mcp_payload["overall"], "no_config")
            self.assertFalse(mcp_payload["security"]["executes_tools"])

            mcp_policy = subprocess.run(
                [
                    str(bin_dir / "lai"),
                    "mcp",
                    "policy-check",
                    "--operation",
                    "call-tool",
                    "--server",
                    "desktop-commander",
                    "--tool",
                    "read_file",
                    "--json",
                ],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            mcp_policy_payload = json.loads(mcp_policy.stdout)
            self.assertEqual(mcp_policy_payload["decision"], "DENY")
            self.assertFalse(mcp_policy_payload["executed"])

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

                    events_request = urllib.request.Request(
                        f"http://127.0.0.1:{control_port}/v1/runs/{control_run_id}/events",
                        headers={"Authorization": f"Bearer {control_secret}"},
                    )
                    with urllib.request.urlopen(events_request, timeout=2) as response:
                        self.assertEqual(response.status, 200)
                        events_payload = json.loads(response.read().decode("utf-8"))
                    self.assertEqual(events_payload["control_run_id"], control_run_id)
                    self.assertTrue(events_payload["terminal"])
                    self.assertEqual(events_payload["status"], "succeeded")
                    event_names = [event["event"] for event in events_payload["events"]]
                    self.assertIn("process_started", event_names)
                    self.assertIn("output_captured", event_names)
                    self.assertIn("finished", event_names)
                    events_text = json.dumps(events_payload, sort_keys=True)
                    self.assertNotIn("fake response", events_text)
                    self.assertNotIn("stdout", events_text)
                    self.assertNotIn("stderr", events_text)
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
            rollback_repo = root / "rollback-repo"
            rollback_repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=rollback_repo, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=rollback_repo, check=True)
            rollback_target = rollback_repo / "result.py"
            rollback_target.write_text("value = 0\n", encoding="utf-8")
            rollback_responder = InstalledSequenceResponder([
                installed_tool_call("read", "read", {"path": "result.py"}),
                installed_tool_call(
                    "edit",
                    "edit",
                    {"path": "result.py", "old": "value = 0", "new": "value = 1"},
                ),
                installed_tool_call(
                    "validate",
                    "bash",
                    {"command": "python3 -m py_compile result.py"},
                ),
                installed_completion("implemented and validated"),
            ])
            with FakeLlamaServer(responder=rollback_responder) as llama:
                rollback_env = {
                    **install_env,
                    "LAI_HOST": llama.host,
                    "LAI_PORT": str(llama.port),
                    "LAI_API_KEY_FILE": str(key_file),
                    "LAI_ALLOW_PROTECTED_BRANCH_WRITES": "1",
                    "LAI_MODEL": "fake-local-model",
                }
                implemented = subprocess.run(
                    [
                        str(bin_dir / "lai"),
                        "implement",
                        "Change result.py value from 0 to 1 and validate it.",
                    ],
                    cwd=rollback_repo,
                    env=rollback_env,
                    text=True,
                    capture_output=True,
                    timeout=20,
                    check=True,
                )
            self.assertIn("implemented and validated", implemented.stdout)
            self.assertEqual(rollback_target.read_text(encoding="utf-8"), "value = 1\n")

            checkpoint = subprocess.run(
                [str(bin_dir / "lai"), "checkpoint", "show", "--last", "--json"],
                cwd=rollback_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            checkpoint_payload = json.loads(checkpoint.stdout)
            rollback_run_id = checkpoint_payload["checkpoint"]["run_id"]
            self.assertEqual(checkpoint_payload["checkpoint"]["tracked_paths"], ["result.py"])

            snapshot = subprocess.run(
                [str(bin_dir / "lai"), "snapshot", "show", rollback_run_id, "--json"],
                cwd=rollback_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            snapshot_payload = json.loads(snapshot.stdout)
            snapshot_text = json.dumps(snapshot_payload)
            self.assertEqual(snapshot_payload["snapshot"]["file_count"], 1)
            self.assertIn("content_bytes", snapshot_text)
            self.assertNotIn("value = 0", snapshot_text)

            dry_run = subprocess.run(
                [str(bin_dir / "lai"), "rollback", rollback_run_id, "--dry-run", "--json"],
                cwd=rollback_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(json.loads(dry_run.stdout)["blocked_count"], 0)
            self.assertEqual(rollback_target.read_text(encoding="utf-8"), "value = 1\n")

            applied = subprocess.run(
                [str(bin_dir / "lai"), "rollback", rollback_run_id, "--json"],
                cwd=rollback_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(json.loads(applied.stdout)["blocked_count"], 0)
            self.assertEqual(rollback_target.read_text(encoding="utf-8"), "value = 0\n")

            rollback_target.write_text("external drift\n", encoding="utf-8")
            blocked = subprocess.run(
                [str(bin_dir / "lai"), "rollback", rollback_run_id, "--dry-run", "--json"],
                cwd=rollback_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            blocked_payload = json.loads(blocked.stdout)
            self.assertGreaterEqual(blocked_payload["blocked_count"], 1)
            self.assertIn("current file hash differs", json.dumps(blocked_payload))

            recovery_clear = subprocess.run(
                [str(bin_dir / "lai"), "recovery", "clear"],
                cwd=rollback_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Recovery checkpoint cleared.", recovery_clear.stdout)
            self.assertIn("Recovery snapshot cleared.", recovery_clear.stdout)
            self.assertNotIn("value = 0", recovery_clear.stdout)

            cleared_checkpoints = subprocess.run(
                [str(bin_dir / "lai"), "checkpoint", "list", "--json"],
                cwd=rollback_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(json.loads(cleared_checkpoints.stdout)["checkpoint_count"], 0)

            missing_snapshot = subprocess.run(
                [str(bin_dir / "lai"), "snapshot", "show", rollback_run_id, "--json"],
                cwd=rollback_repo,
                env=install_env,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(missing_snapshot.returncode, 0)
            self.assertIn("snapshot not found", missing_snapshot.stderr)

            readiness = subprocess.run(
                [str(bin_dir / "lai"), "readiness", "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            readiness_payload = json.loads(readiness.stdout)
            self.assertEqual(readiness_payload["version"], EXPECTED_VERSION)
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
            self.assertEqual(release_payload["version"], EXPECTED_VERSION)
            self.assertIn("release_safety", {item["name"] for item in release_payload["checks"]})

            release_pack = subprocess.run(
                [
                    str(bin_dir / "lai"),
                    "release-pack",
                    "--target",
                    EXPECTED_VERSION,
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
            self.assertEqual(release_pack_payload["version"], EXPECTED_VERSION)
            self.assertTrue(Path(release_pack_payload["files"]["release_body"]).is_file())

            governance = subprocess.run(
                [
                    str(bin_dir / "lai"),
                    "release-governance",
                    "--target",
                    EXPECTED_VERSION,
                    "--json",
                ],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            governance_payload = json.loads(governance.stdout)
            self.assertEqual(governance_payload["version"], EXPECTED_VERSION)
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
            self.assertEqual(alias_governance_payload["version"], EXPECTED_VERSION)
            self.assertIn("github_release", {item["id"] for item in alias_governance_payload["manual_actions"]})

            project_handoff = subprocess.run(
                [
                    str(bin_dir / "lai"),
                    "project-handoff",
                    "--target",
                    EXPECTED_VERSION,
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
            self.assertEqual(project_handoff_payload["version"], EXPECTED_VERSION)
            self.assertTrue(Path(project_handoff_payload["files"]["markdown"]).is_file())

            next_chat = subprocess.run(
                [str(bin_dir / "lai"), "next-chat", "--target", EXPECTED_VERSION, "--json"],
                cwd=sample_repo,
                env=install_env,
                text=True,
                capture_output=True,
                check=True,
            )
            next_chat_payload = json.loads(next_chat.stdout)
            self.assertEqual(next_chat_payload["version"], EXPECTED_VERSION)
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


    def test_server_start_allows_already_running_secure_server_without_windows_launcher(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            key_file = root / "key"
            key_file.write_text("synthetic-test-key")

            with FakeLlamaServer() as secure_server:
                result = subprocess.run(
                    [str(REPO / "scripts" / "ministral-start")],
                    env={
                        **os.environ,
                        "LAI_HOST": secure_server.host,
                        "LAI_PORT": str(secure_server.port),
                        "LAI_API_KEY_FILE": str(key_file),
                    },
                    text=True,
                    capture_output=True,
                )

            self.assertEqual(result.returncode, 0)
            self.assertIn("already running securely", result.stdout)
            self.assertNotIn("LAI_WINDOWS_LAUNCHER", result.stderr)
            self.assertNotIn("synthetic-test-key", result.stdout + result.stderr)

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

    def test_model_server_scripts_do_not_put_api_keys_in_curl_arguments(self):
        start_source = (REPO / "scripts" / "ministral-start").read_text(encoding="utf-8")
        doctor_source = (REPO / "scripts" / "ministral-doctor").read_text(encoding="utf-8")
        combined = start_source + "\n" + doctor_source

        self.assertNotIn('api_key="$(tr -d', combined)
        self.assertNotIn('Authorization: Bearer ${api_key}', combined)
        self.assertIn('python3 - "$host" "$port" "$key_file"', start_source)
        self.assertIn('python3 - "$host" "$port" "$key_file"', doctor_source)

    def test_model_server_start_auto_discovers_windows_launcher_without_secret_values(self):
        source = (REPO / "scripts" / "ministral-start").read_text(encoding="utf-8")

        self.assertIn('script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"', source)
        self.assertIn('candidate="$script_dir/start-secure.ps1"', source)
        self.assertIn('key_file_windows=$(wsl_to_windows_path "$key_file")', source)
        self.assertIn('detect_llama_server()', source)
        self.assertIn('Get-Command llama-server.exe', source)
        self.assertIn('LAI_BOOTSTRAP_LLAMA_SERVER="$llama_server"', source)
        self.assertIn('LAI_BOOTSTRAP_KEY_FILE_WINDOWS="$key_file_windows"', source)
        self.assertIn('PS_BOOTSTRAP_PATH="$ps_bootstrap"', source)
        self.assertIn('trap cleanup_ps_bootstrap EXIT', source)
        self.assertIn('powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$ps_bootstrap_windows"', source)
        self.assertNotIn('-File "$windows_launcher"', source)
        self.assertNotIn('synthetic-test-key', source)

    def test_windows_secure_launcher_accepts_local_model_files_without_key_argument_fallback(self):
        source = (REPO / "scripts" / "start-secure.ps1").read_text(encoding="utf-8")

        self.assertIn("Test-Path -LiteralPath $model -PathType Leaf", source)
        self.assertIn('$argsList += @("--model", $model)', source)
        self.assertIn('$argsList += @("-hf", $model, "--no-mmproj")', source)
        self.assertIn('$ctxSize = if ($env:LAI_CTX_SIZE)', source)
        self.assertIn('$gpuLayers = if ($env:LAI_GPU_LAYERS)', source)
        self.assertIn('$argsList += @("--api-key-file", $keyFile)', source)
        self.assertNotIn('Get-Content $keyFile -Raw', source)
        self.assertNotIn('$argsList += @("--api-key",', source)


if __name__ == "__main__":
    unittest.main()
