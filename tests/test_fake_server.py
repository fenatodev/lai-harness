import importlib.util
import io
from importlib.machinery import SourceFileLoader
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest import mock

from fake_llama_server import FakeLlamaServer


SOURCE = Path(__file__).parents[1] / "src" / "local-agent"
if str(SOURCE.parent) not in sys.path:
    sys.path.insert(0, str(SOURCE.parent))
SPEC = importlib.util.spec_from_loader(
    "lai_fake_server_agent",
    SourceFileLoader("lai_fake_server_agent", str(SOURCE)),
)
agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent)


class FakeServerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.key_file = self.root / "key"
        self.key_file.write_text("synthetic-test-key")
        agent.CONFIG["api_key_file"] = self.key_file

    def tearDown(self):
        self.temp.cleanup()

    def test_props_rejects_missing_bearer_and_accepts_configured_key(self):
        with FakeLlamaServer() as server:
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(f"http://{server.host}:{server.port}/props")
            self.assertEqual(caught.exception.code, 401)
            request = urllib.request.Request(
                f"http://{server.host}:{server.port}/props",
                headers={"Authorization": "Bearer synthetic-test-key"},
            )
            with urllib.request.urlopen(request) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(json.load(response)["model"], "fake-local-model")

    def test_agent_readiness_and_chat_completion_use_configured_server(self):
        with FakeLlamaServer() as server:
            old_port = agent.LLAMA_PORT
            agent.LLAMA_PORT = server.port
            agent.METRICS_DIR = self.root / "metrics"
            agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
            try:
                self.assertTrue(agent.server_ready(server.host))
                result = agent.api_call(
                    server.host,
                    [{"role": "user", "content": "hello"}],
                    use_tools=False,
                )
            finally:
                agent.LLAMA_PORT = old_port
            self.assertEqual(result["choices"][0]["message"]["content"], "fake response")
            chat = next(item for item in server.requests if item[0] == "POST")
            self.assertEqual(chat[2]["Authorization"], "Bearer synthetic-test-key")
            self.assertEqual(chat[3]["model"], agent.MODEL)


    def test_api_call_normalizes_tool_history_for_strict_chat_templates(self):
        def assert_strict(payload, requests):
            roles = [message.get("role") for message in payload["messages"]]
            if "tool" in roles:
                return 500, {"error": {"message": "tool role leaked"}}
            if roles != ["system", "user", "assistant", "user"]:
                return 500, {"error": {"message": "bad roles: " + ",".join(roles)}}
            tool_result = payload["messages"][-1]["content"]
            if "TOOL RESULTS" not in tool_result or "git status" not in tool_result or "FOLLOW-UP" not in tool_result:
                return 500, {"error": {"message": "missing compact coalesced tool evidence"}}
            return {
                "choices": [{"message": {"role": "assistant", "content": "ok"}}],
                "usage": {"prompt_tokens": 11, "completion_tokens": 1, "total_tokens": 12},
            }

        messages = [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "task"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call-1",
                        "type": "function",
                        "function": {"name": "git", "arguments": "{\"operation\":\"changes\"}"},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "call-1", "name": "git", "content": "git status: clean"},
            {"role": "user", "content": "FOLLOW-UP: answer from tool evidence."},
        ]

        with FakeLlamaServer(responder=assert_strict) as server:
            old_port = agent.LLAMA_PORT
            old_metrics_dir = agent.METRICS_DIR
            old_metrics_file = agent.METRICS_FILE
            agent.LLAMA_PORT = server.port
            agent.METRICS_DIR = self.root / "metrics"
            agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
            try:
                result = agent.api_call(server.host, messages, tools=[{"type": "function", "function": {"name": "git", "parameters": {"type": "object"}}}])
            finally:
                agent.LLAMA_PORT = old_port
                agent.METRICS_DIR = old_metrics_dir
                agent.METRICS_FILE = old_metrics_file

        self.assertEqual(result["choices"][0]["message"]["content"], "ok")
        posted = next(item for item in server.requests if item[0] == "POST")[3]
        self.assertNotIn('"role": "tool"', json.dumps(posted))
        self.assertIn("TOOL REQUESTS", posted["messages"][2]["content"])
        self.assertIn("TOOL RESULTS", posted["messages"][3]["content"])

    def test_api_call_reports_http_errors_without_traceback_or_secrets(self):
        def bad_request(payload, requests):
            return 400, {
                "error": {
                    "message": "invalid request for Bearer synthetic-test-key at /" + "home/example/private",
                    "type": "invalid_request",
                }
            }

        with FakeLlamaServer(responder=bad_request) as server:
            old_port = agent.LLAMA_PORT
            old_metrics_dir = agent.METRICS_DIR
            old_metrics_file = agent.METRICS_FILE
            agent.LLAMA_PORT = server.port
            agent.METRICS_DIR = self.root / "metrics"
            agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
            try:
                with self.assertRaises(agent.ModelAPIError) as caught:
                    agent.api_call(
                        server.host,
                        [{"role": "user", "content": "hello"}],
                        use_tools=False,
                    )
            finally:
                agent.LLAMA_PORT = old_port
                agent.METRICS_DIR = old_metrics_dir
                agent.METRICS_FILE = old_metrics_file
        text = str(caught.exception)
        self.assertIn("model API HTTP 400", text)
        self.assertIn("invalid request", text)
        self.assertNotIn("synthetic-test-key", text)
        self.assertNotIn("Bearer synthetic", text)
        self.assertNotIn("/" + "home/example", text)

    def test_lifecycle_prints_model_api_error_without_python_traceback(self):
        with mock.patch.object(agent, "main", side_effect=agent.ModelAPIError("model API HTTP 400: bad request")), \
                mock.patch.object(agent, "finalize_run_checkpoint") as finalize, \
                mock.patch("sys.stderr", new_callable=io.StringIO) as stderr:
            with self.assertRaises(SystemExit) as caught:
                agent.run_main_with_checkpoint_lifecycle()
        self.assertEqual(caught.exception.code, 1)
        self.assertIn("MODEL_API_ERROR: model API HTTP 400: bad request", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())
        finalize.assert_called_once_with("failed", reason="ModelAPIError")

    def test_connection_failure_is_reported(self):
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        sock.close()
        old_port = agent.LLAMA_PORT
        agent.LLAMA_PORT = port
        try:
            with self.assertRaises(urllib.error.URLError):
                agent.server_ready("127.0.0.1")
        finally:
            agent.LLAMA_PORT = old_port

    def test_doctor_passes_against_fake_server(self):
        doctor = Path(__file__).parents[1] / "scripts" / "ministral-doctor"
        with FakeLlamaServer() as server:
            env = {
                **os.environ,
                "LAI_HOST": server.host,
                "LAI_PORT": str(server.port),
                "LAI_API_KEY_FILE": str(self.key_file),
            }
            result = subprocess.run(
                [str(doctor)],
                text=True,
                capture_output=True,
                env=env,
                check=True,
            )
        self.assertIn("Authentication: OK", result.stdout)
        self.assertIn(f"{server.host}:{server.port}", result.stdout)

    def test_python_doctor_accepts_cli_host_port_and_key(self):
        with FakeLlamaServer() as server:
            result = subprocess.run(
                [
                    str(SOURCE),
                    "--host", server.host,
                    "--port", str(server.port),
                    "--api-key-file", str(self.key_file),
                    "--doctor",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
        self.assertIn("Authentication: OK", result.stdout)
        self.assertIn(f"{server.host}:{server.port}", result.stdout)

    def test_text_post_patch_sanity_does_not_require_model(self):
        repo = self.root / "repo"
        repo.mkdir()

        target = repo / "notes.txt"
        target.write_text("before\n")

        subprocess.run(
            ["git", "init", "-q"],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            ["git", "add", "notes.txt"],
            cwd=repo,
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-qm",
                "base",
            ],
            cwd=repo,
            check=True,
        )

        target.write_text("after\n")

        old_root = agent.ROOT
        agent.ROOT = repo

        try:
            result = agent.post_patch_sanity(
                "unused",
                "check notes",
                ["notes.txt"],
            )
        finally:
            agent.ROOT = old_root

        self.assertIsNone(result)



if __name__ == "__main__":
    unittest.main()
