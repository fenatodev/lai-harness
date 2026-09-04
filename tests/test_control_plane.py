import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock


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
                "model_execution": False,
                "shell_execution": False,
                "repository_write": False,
                "policy_classification": True,
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
            self.assertFalse(payload["capabilities"]["model_execution"])
            self.assertFalse(payload["capabilities"]["shell_execution"])

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
        self.assertEqual(status, 405)
        self.assertEqual(payload["error"]["code"], "method_not_allowed")

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
