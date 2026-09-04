import importlib.util
import os
import socket
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest import mock

from fake_llama_server import FakeLlamaServer


SOURCE = Path(__file__).parents[1] / "src" / "local-agent"
SPEC = importlib.util.spec_from_loader(
    "lai_control_test_agent",
    SourceFileLoader("lai_control_test_agent", str(SOURCE)),
)
agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent)


class ControlPlaneTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        agent.ROOT = self.root.resolve()
        agent.CONFIG["control_api_key_file"] = self.base / "config" / "control-api-key"
        agent.METRICS_DIR = self.base / "data" / "metrics"
        agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
        agent.AUDIT_DIR = self.base / "data" / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
        self.token = "synthetic-control-token"
        self.server = agent.create_control_server("127.0.0.1", 0, token=self.token)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, path, *, method="GET", token=None, body=None, content_type="application/json"):
        headers = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        data = None
        if body is not None:
            data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
            headers["Content-Type"] = content_type
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            method=method,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                status = response.status
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            status = exc.code
            payload = json.loads(exc.read().decode("utf-8"))
        return status, payload

    def test_control_token_init_is_separate_secret_and_restrictive(self):
        path = Path(agent.CONFIG["control_api_key_file"])
        result = agent.init_control_api_token()
        self.assertTrue(path.is_file())
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertFalse(result["secret_printed"])
        token = path.read_text(encoding="utf-8").strip()
        self.assertGreater(len(token), 32)
        self.assertNotIn(token, json.dumps(result))
        self.assertEqual(agent.control_api_key(), token)
        with self.assertRaisesRegex(SystemExit, "already exists"):
            agent.init_control_api_token()
        replaced = agent.init_control_api_token(force=True)
        self.assertTrue(replaced["replaced"])
        self.assertNotEqual(path.read_text(encoding="utf-8").strip(), token)
        path.chmod(0o644)
        with self.assertRaisesRegex(RuntimeError, "unsafe"):
            agent.control_api_key()

        safe_target = self.base / "safe-target"
        safe_target.write_text("safe-token\n", encoding="utf-8")
        safe_target.chmod(0o600)
        path.unlink()
        path.symlink_to(safe_target)
        with self.assertRaisesRegex(RuntimeError, "unsafe"):
            agent.control_api_key()

    def test_control_token_config_default_and_cli_status_do_not_print_secret(self):
        values, _ = agent.load_configuration([], environ={}, home=self.root)
        self.assertEqual(
            values["control_api_key_file"],
            self.root / ".config" / "lai" / "control-api-key",
        )
        result = agent.init_control_api_token(path=self.base / "explicit-key")
        self.assertFalse(result["secret_printed"])
        shown = agent.render_control_token(["status", "--json"])
        self.assertNotIn("synthetic-control-token", shown)

    def test_server_refuses_non_loopback_binding(self):
        self.assertTrue(agent.control_bind_is_loopback("127.0.0.1"))
        self.assertTrue(agent.control_bind_is_loopback("localhost"))
        self.assertFalse(agent.control_bind_is_loopback("0.0.0.0"))
        with self.assertRaisesRegex(ValueError, "loopback"):
            agent.create_control_server("0.0.0.0", 0, token=self.token)
    def test_protected_endpoints_require_bearer_auth(self):
        status, payload = self.request("/v1/status")
        self.assertEqual(status, 401)
        self.assertEqual(payload["error"]["code"], "unauthorized")
        self.assertNotIn(self.token, json.dumps(payload))

        status, payload = self.request("/v1/status", token="wrong")
        self.assertEqual(status, 401)
        self.assertNotIn(self.token, json.dumps(payload))

    def test_status_readiness_and_runs_are_read_only_json(self):
        fake_status = {
            "product": agent.PRODUCT_NAME,
            "version": agent.VERSION,
            "repository": str(self.root),
            "capabilities": {
                "model_execution": True,
                "shell_execution": False,
                "repository_write": False,
                "policy_classification": True,
                "async_read_only_runs": True,
                "remote_tool_profile": "shell-free-read-only",
                "allowed_run_modes": ["plan", "review", "security", "diagnose", "release"],
            },
        }
        fake_readiness = {"overall": "ready", "checks": []}
        fake_runs = [{"run_id": "run-1", "status": "completed"}]
        with mock.patch.object(agent, "control_status_payload", return_value=fake_status), \
                mock.patch.object(agent, "collect_readiness_status", return_value=fake_readiness), \
                mock.patch.object(agent, "collect_run_history", return_value=fake_runs), \
                mock.patch.object(agent, "run_history_public_record", side_effect=lambda run: run):
            status_code, payload = self.request("/v1/status", token=self.token)
            self.assertEqual(status_code, 200)
            self.assertTrue(payload["capabilities"]["model_execution"])
            self.assertFalse(payload["capabilities"]["shell_execution"])
            self.assertTrue(payload["capabilities"]["async_read_only_runs"])
            self.assertEqual(payload["capabilities"]["remote_tool_profile"], "shell-free-read-only")

            status_code, payload = self.request("/v1/readiness", token=self.token)
            self.assertEqual(status_code, 200)
            self.assertEqual(payload["overall"], "ready")

            status_code, payload = self.request("/v1/runs?limit=1", token=self.token)
            self.assertEqual(status_code, 200)
            self.assertEqual(payload["runs"][0]["run_id"], "run-1")

    def test_policy_endpoint_classifies_without_execution(self):
        status, payload = self.request(
            "/v1/policy-check",
            method="POST",
            token=self.token,
            body={"tool": "bash", "args": {"command": "npm publish"}, "mode": "release"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["decision"], "DENY")
        self.assertFalse(payload["executed"])
    def test_malformed_unsupported_and_oversized_requests_fail_safely(self):
        status, payload = self.request(
            "/v1/policy-check",
            method="POST",
            token=self.token,
            body=b"{bad json",
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_request")

        status, payload = self.request(
            "/v1/policy-check",
            method="POST",
            token=self.token,
            body=b"{}",
            content_type="text/plain",
        )
        self.assertEqual(status, 415)
        self.assertEqual(payload["error"]["code"], "unsupported_media_type")

        status, payload = self.request(
            "/v1/policy-check",
            method="POST",
            token=self.token,
            body=b"x" * (agent.CONTROL_API_MAX_BODY_BYTES + 1),
        )
        self.assertEqual(status, 413)
        self.assertEqual(payload["error"]["code"], "payload_too_large")
        status, payload = self.request(
            "/v1/runs",
            method="POST",
            token=self.token,
            body={},
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload["error"]["code"], "invalid_run_request")

        status, payload = self.request(
            "/v1/status",
            method="PUT",
            token=self.token,
            body={},
        )
        self.assertEqual(status, 405)
        self.assertEqual(payload["error"]["code"], "method_not_allowed")

        status, payload = self.request("/v1/does-not-exist", token=self.token)
        self.assertEqual(status, 404)
        self.assertEqual(payload["error"]["code"], "not_found")

    def wait_run(self, control_run_id, statuses, timeout=3):
        wanted = {statuses} if isinstance(statuses, str) else set(statuses)
        deadline = time.monotonic() + timeout
        last = None
        while time.monotonic() < deadline:
            status, payload = self.request(
                f"/v1/runs/{control_run_id}", token=self.token
            )
            self.assertEqual(status, 200)
            last = payload["run"]
            if last["status"] in wanted:
                return last
            time.sleep(0.02)
        self.fail(f"control run did not reach {sorted(wanted)}; last={last}")

    def test_async_run_rejects_non_shell_free_modes_and_invalid_requests(self):
        for mode in (
            "general", "implement", "fix", "ci-fix", "refactor",
            "debug", "test",
        ):
            status, payload = self.request(
                "/v1/runs",
                method="POST",
                token=self.token,
                body={"mode": mode, "task": "inspect safely"},
            )
            self.assertEqual(status, 400, mode)
            self.assertEqual(payload["error"]["code"], "invalid_run_request")

        for body in (
            {"mode": "plan", "task": ""},
            {"mode": "plan", "task": "x" * (agent.CONTROL_RUN_TASK_MAX_CHARS + 1)},
            {"mode": "plan", "task": "ok", "command": "rm -rf /"},
            {"mode": "plan", "task": "bad\x00task"},
        ):
            status, payload = self.request(
                "/v1/runs", method="POST", token=self.token, body=body
            )
            self.assertEqual(status, 400)
            self.assertEqual(payload["error"]["code"], "invalid_run_request")

    def test_remote_capability_profiles_are_shell_free_and_preserve_local_modes(self):
        self.assertIn("bash", agent.tool_names_for_mode("diagnose"))
        self.assertIn("bash", agent.tool_names_for_mode("release"))

        for mode in agent.CONTROL_RUN_ALLOWED_MODES:
            names = agent.tool_names_for_mode(mode, remote_control_child=True)
            self.assertTrue(names, mode)
            self.assertFalse(names & agent.CONTROL_RUN_FORBIDDEN_TOOL_NAMES, mode)

        self.assertEqual(
            agent.tool_names_for_mode("diagnose", remote_control_child=True),
            {"project", "read", "inspect", "search", "list", "git"},
        )
        self.assertEqual(
            agent.tool_names_for_mode("release", remote_control_child=True),
            {"project", "read", "inspect", "search", "list", "git"},
        )
        with self.assertRaisesRegex(ValueError, "no remote control capability profile"):
            agent.tool_names_for_mode("implement", remote_control_child=True)

    def test_remote_diagnose_and_release_model_schemas_exclude_shell_and_writes(self):
        key_file = self.base / "profile-llama-key"
        key_file.write_text("synthetic-test-key", encoding="utf-8")
        forbidden = agent.CONTROL_RUN_FORBIDDEN_TOOL_NAMES

        for mode in ("diagnose", "release"):
            with self.subTest(mode=mode):
                state_dir = self.base / f"{mode}-state"
                metrics_dir = self.base / f"{mode}-metrics"
                audit_dir = self.base / f"{mode}-audit"
                with FakeLlamaServer() as llama, mock.patch.dict(
                    os.environ,
                    {
                        "LAI_HOST": llama.host,
                        "LAI_PORT": str(llama.port),
                        "LAI_API_KEY_FILE": str(key_file),
                        "LAI_STATE_DIR": str(state_dir),
                        "LAI_METRICS_DIR": str(metrics_dir),
                        "LAI_AUDIT_DIR": str(audit_dir),
                    },
                    clear=False,
                ):
                    status, payload = self.request(
                        "/v1/runs",
                        method="POST",
                        token=self.token,
                        body={"mode": mode, "task": f"give a concise {mode} assessment"},
                    )
                    self.assertEqual(status, 202)
                    self.assertEqual(payload["run"]["tool_profile"], "shell-free-read-only")
                    final = self.wait_run(
                        payload["run"]["control_run_id"],
                        {"succeeded", "failed"},
                        timeout=8,
                    )
                    posts = [
                        item for item in llama.requests
                        if item[0] == "POST" and item[1] == "/v1/chat/completions"
                    ]

                self.assertEqual(final["status"], "succeeded", final["stderr"])
                self.assertTrue(posts, mode)
                tool_names = {
                    tool["function"]["name"]
                    for tool in (posts[0][3].get("tools") or [])
                }
                self.assertFalse(tool_names & forbidden, (mode, tool_names))
                self.assertIn("git", tool_names)
                self.assertIn("inspect", tool_names)

    def test_source_tree_control_child_uses_checked_in_skills_without_overriding_explicit_config(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            env = agent.control_run_child_env()
        self.assertEqual(
            env.get("LAI_SKILLS_DIR"),
            str(SOURCE.resolve().parent.parent / "skills"),
        )
        self.assertEqual(env.get(agent.CONTROL_RUN_CHILD_ENV), "1")

        explicit = str(self.base / "explicit-skills")
        with mock.patch.dict(os.environ, {"LAI_SKILLS_DIR": explicit}, clear=True):
            env = agent.control_run_child_env()
        self.assertEqual(env.get("LAI_SKILLS_DIR"), explicit)

    def test_async_run_uses_fixed_subprocess_and_reports_bounded_result(self):
        calls = []

        class FakeProcess:
            def __init__(self, argv, **kwargs):
                calls.append((list(argv), dict(kwargs)))
                self.returncode = None
                self.done = threading.Event()
                kwargs["stdout"].write(b"mobile plan result\n")
                kwargs["stderr"].write(b"")
                threading.Timer(0.05, self.finish).start()

            def finish(self):
                self.returncode = 0
                self.done.set()

            def poll(self):
                return self.returncode

            def wait(self, timeout=None):
                self.done.wait(timeout)
                return self.returncode

            def terminate(self):
                self.returncode = -15
                self.done.set()

            def kill(self):
                self.returncode = -9
                self.done.set()

        task = "prepare a read-only implementation plan"
        with mock.patch.object(agent.subprocess, "Popen", FakeProcess):
            status, payload = self.request(
                "/v1/runs",
                method="POST",
                token=self.token,
                body={"mode": "plan", "task": task},
            )
            self.assertEqual(status, 202)
            control_run_id = payload["run"]["control_run_id"]
            self.assertNotIn(task, json.dumps(payload))
            final = self.wait_run(control_run_id, "succeeded")

        self.assertEqual(final["exit_code"], 0)
        self.assertIn("mobile plan result", final["stdout"])
        self.assertFalse(final["stdout_truncated"])
        self.assertEqual(len(calls), 1)
        argv, kwargs = calls[0]
        self.assertEqual(
            argv,
            [sys.executable, str(SOURCE.resolve()), "--plan", task],
        )
        self.assertEqual(kwargs["cwd"], str(self.root.resolve()))
        self.assertIs(kwargs["stdin"], subprocess.DEVNULL)
        self.assertFalse(kwargs["shell"])
        self.assertTrue(kwargs["start_new_session"])
        self.assertIsInstance(kwargs["env"], dict)
        self.assertEqual(kwargs["env"][agent.CONTROL_RUN_CHILD_ENV], "1")

    def test_async_run_real_subprocess_completes_against_fake_llama(self):
        key_file = self.base / "llama-key"
        key_file.write_text("synthetic-test-key", encoding="utf-8")
        state_dir = self.base / "child-state"
        metrics_dir = self.base / "child-metrics"
        audit_dir = self.base / "child-audit"
        before = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout

        with FakeLlamaServer() as llama, mock.patch.dict(
            os.environ,
            {
                "LAI_HOST": llama.host,
                "LAI_PORT": str(llama.port),
                "LAI_API_KEY_FILE": str(key_file),
                "LAI_STATE_DIR": str(state_dir),
                "LAI_METRICS_DIR": str(metrics_dir),
                "LAI_AUDIT_DIR": str(audit_dir),
            },
            clear=False,
        ):
            status, payload = self.request(
                "/v1/runs",
                method="POST",
                token=self.token,
                body={"mode": "plan", "task": "return a concise read-only plan"},
            )
            self.assertEqual(status, 202)
            final = self.wait_run(
                payload["run"]["control_run_id"],
                {"succeeded", "failed"},
                timeout=8,
            )

        self.assertEqual(final["status"], "succeeded", final["stderr"])
        self.assertEqual(final["exit_code"], 0)
        self.assertIn("fake response", final["stdout"])
        self.assertGreaterEqual(
            sum(1 for method, path, _, _ in llama.requests if method == "POST" and path == "/v1/chat/completions"),
            1,
        )
        after = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        self.assertEqual(after, before)

    def test_control_child_never_autostarts_model_service(self):
        key_file = self.base / "offline-key"
        key_file.write_text("synthetic-test-key", encoding="utf-8")
        marker = self.base / "launcher-called"
        launcher = self.base / "launcher.sh"
        launcher.write_text(
            "#!/usr/bin/env bash\nprintf called > \"$1\"\n",
            encoding="utf-8",
        )
        launcher.chmod(0o755)
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            unused_port = probe.getsockname()[1]

        env = {
            **os.environ,
            "LAI_HOST": "127.0.0.1",
            "LAI_PORT": str(unused_port),
            "LAI_API_KEY_FILE": str(key_file),
            "LAI_DATA_DIR": str(self.base / "offline-data"),
            "LAI_SERVER_LAUNCHER": str(launcher),
            agent.CONTROL_RUN_CHILD_ENV: "1",
        }
        result = subprocess.run(
            [str(SOURCE), "--plan", "inspect without starting services"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=5,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("control runs do not auto-start services", result.stderr)
        self.assertFalse(marker.exists())

    def test_control_run_queue_is_serial_and_bounded(self):
        first_release = threading.Event()
        calls = []

        class FakeProcess:
            def __init__(self, argv, **kwargs):
                self.index = len(calls)
                calls.append(self)
                self.returncode = None
                self.done = threading.Event()
                kwargs["stdout"].write(f"run-{self.index}\n".encode())
                if self.index == 0:
                    threading.Thread(target=self._wait_first, daemon=True).start()
                else:
                    self.returncode = 0
                    self.done.set()

            def _wait_first(self):
                first_release.wait(3)
                if self.returncode is None:
                    self.returncode = 0
                    self.done.set()

            def poll(self):
                return self.returncode

            def wait(self, timeout=None):
                self.done.wait(timeout)
                return self.returncode

            def terminate(self):
                self.returncode = -15
                self.done.set()

            def kill(self):
                self.returncode = -9
                self.done.set()

        accepted = []
        with mock.patch.object(agent.subprocess, "Popen", FakeProcess):
            status, payload = self.request(
                "/v1/runs", method="POST", token=self.token,
                body={"mode": "plan", "task": "first"},
            )
            self.assertEqual(status, 202)
            accepted.append(payload["run"]["control_run_id"])
            self.wait_run(accepted[0], "running")

            for index in range(agent.CONTROL_RUN_QUEUE_LIMIT):
                status, payload = self.request(
                    "/v1/runs", method="POST", token=self.token,
                    body={"mode": "review", "task": f"queued-{index}"},
                )
                self.assertEqual(status, 202)
                accepted.append(payload["run"]["control_run_id"])
            self.assertEqual(len(calls), 1)

            status, payload = self.request(
                "/v1/runs", method="POST", token=self.token,
                body={"mode": "security", "task": "overflow"},
            )
            self.assertEqual(status, 429)
            self.assertEqual(payload["error"]["code"], "queue_full")

            first_release.set()
            for run_id in accepted:
                self.wait_run(run_id, "succeeded")

        self.assertEqual(len(calls), 1 + agent.CONTROL_RUN_QUEUE_LIMIT)

    def test_control_run_cancellation_is_scoped_to_run_lifecycle(self):
        first_release = threading.Event()
        calls = []

        class BlockingProcess:
            def __init__(self, argv, **kwargs):
                calls.append(self)
                self.returncode = None
                self.done = threading.Event()
                self.terminated = False
                threading.Thread(target=self._hold, daemon=True).start()

            def _hold(self):
                first_release.wait(3)
                if self.returncode is None:
                    self.returncode = 0
                    self.done.set()

            def poll(self):
                return self.returncode

            def wait(self, timeout=None):
                self.done.wait(timeout)
                return self.returncode

            def terminate(self):
                self.terminated = True
                self.returncode = -15
                self.done.set()

            def kill(self):
                self.returncode = -9
                self.done.set()

        with mock.patch.object(agent.subprocess, "Popen", BlockingProcess):
            status, first = self.request(
                "/v1/runs", method="POST", token=self.token,
                body={"mode": "plan", "task": "running"},
            )
            first_id = first["run"]["control_run_id"]
            self.wait_run(first_id, "running")
            status, second = self.request(
                "/v1/runs", method="POST", token=self.token,
                body={"mode": "review", "task": "queued"},
            )
            second_id = second["run"]["control_run_id"]

            status, payload = self.request(
                f"/v1/runs/{second_id}", method="DELETE", token=self.token
            )
            self.assertEqual(status, 200)
            self.assertEqual(payload["run"]["status"], "cancelled")
            self.assertEqual(len(calls), 1)

            status, payload = self.request(
                f"/v1/runs/{first_id}", method="DELETE", token=self.token
            )
            self.assertEqual(status, 202)
            final = self.wait_run(first_id, "cancelled")
            self.assertTrue(final["cancel_requested"])
            self.assertTrue(calls[0].terminated)

            status, payload = self.request(
                f"/v1/runs/{first_id}", method="DELETE", token=self.token
            )
            self.assertEqual(status, 409)
            self.assertEqual(payload["error"]["code"], "run_not_cancellable")

            status, payload = self.request(
                "/v1/status", method="DELETE", token=self.token
            )
            self.assertEqual(status, 405)
            first_release.set()

    def test_control_run_output_and_record_retention_are_bounded(self):
        class InstantProcess:
            def __init__(self, argv, **kwargs):
                self.returncode = 0
                kwargs["stdout"].write(b"A" * 80 + b"TAIL")
                kwargs["stderr"].write(b"B" * 80 + b"ERR")

            def poll(self):
                return self.returncode

            def wait(self, timeout=None):
                return self.returncode

            def terminate(self):
                self.returncode = -15

            def kill(self):
                self.returncode = -9

        with mock.patch.object(agent, "CONTROL_RUN_OUTPUT_LIMIT_BYTES", 32), \
                mock.patch.object(agent.subprocess, "Popen", InstantProcess):
            ids = []
            for index in range(agent.CONTROL_RUN_RETAIN_LIMIT + 3):
                record = agent.control_submit_run(
                    self.server,
                    {"mode": "plan", "task": f"retention-{index}"},
                )
                ids.append(record["control_run_id"])
                self.wait_run(ids[-1], "succeeded")
            final = agent.control_run_public_record(self.server, ids[-1])

        self.assertTrue(final["stdout_truncated"])
        self.assertTrue(final["stderr_truncated"])
        self.assertTrue(final["stdout"].endswith("TAIL"))
        self.assertTrue(final["stderr"].endswith("ERR"))
        with self.server.control_run_lock:
            self.assertLessEqual(
                len(self.server.control_run_records),
                agent.CONTROL_RUN_RETAIN_LIMIT,
            )
        self.assertIsNone(agent.control_run_public_record(self.server, ids[0]))

    def test_control_server_close_terminates_active_child(self):
        started = threading.Event()
        process_box = []

        class BlockingProcess:
            def __init__(self, argv, **kwargs):
                self.returncode = None
                self.done = threading.Event()
                self.terminated = False
                process_box.append(self)
                started.set()

            def poll(self):
                return self.returncode

            def wait(self, timeout=None):
                self.done.wait(timeout)
                return self.returncode

            def terminate(self):
                self.terminated = True
                self.returncode = -15
                self.done.set()

            def kill(self):
                self.returncode = -9
                self.done.set()

        extra = agent.create_control_server("127.0.0.1", 0, token=self.token)
        try:
            with mock.patch.object(agent.subprocess, "Popen", BlockingProcess):
                agent.control_submit_run(extra, {"mode": "plan", "task": "hold"})
                self.assertTrue(started.wait(1))
                extra.server_close()
                self.assertTrue(process_box[0].terminated)
                self.assertFalse(extra.control_run_worker.is_alive())
        finally:
            extra.server_close()

    def test_serve_cli_fails_cleanly_when_token_is_missing(self):
        env = {
            **__import__("os").environ,
            "LAI_CONTROL_API_KEY_FILE": str(self.base / "missing-control-token"),
        }
        result = subprocess.run(
            [str(SOURCE.parent / "lai"), "serve", "--port", "8765"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=3,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("control API token not found", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_serve_parser_rejects_public_bind_and_invalid_port(self):
        self.assertEqual(
            agent.parse_control_serve_args(["--bind", "localhost", "--port", "9000"]),
            {"bind": "localhost", "port": 9000},
        )
        with self.assertRaisesRegex(SystemExit, "loopback-only"):
            agent.parse_control_serve_args(["--bind", "0.0.0.0"])
        with self.assertRaisesRegex(SystemExit, "between 1 and 65535"):
            agent.parse_control_serve_args(["--port", "0"])


if __name__ == "__main__":
    unittest.main()
