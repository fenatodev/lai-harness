import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from fake_llama_server import FakeLlamaServer


REPO = Path(__file__).parents[1]
AGENT = REPO / "src" / "local-agent"


def completion(content):
    return {
        "choices": [{"message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13},
    }


def tool_call(call_id, name, arguments):
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


class SequenceResponder:
    def __init__(self, responses):
        self.responses = list(responses)
        self.payloads = []

    def __call__(self, payload, requests):
        self.payloads.append(payload)
        if not self.responses:
            raise AssertionError("fake response sequence exhausted")
        response = self.responses.pop(0)
        return response(payload) if callable(response) else response


class GuardIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.data = self.base / "data"
        self.repo.mkdir()
        shutil.copytree(REPO / "skills", self.data / "skills")
        self.key = self.base / "key"
        self.key.write_text("synthetic-test-key")
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)

    def tearDown(self):
        self.temp.cleanup()

    def run_agent(self, server, *args):
        env = {
            **os.environ,
            "LAI_HOST": server.host,
            "LAI_PORT": str(server.port),
            "LAI_API_KEY_FILE": str(self.key),
            "LAI_DATA_DIR": str(self.data),
            "LAI_MODEL": "fake-local-model",
        }
        return subprocess.run(
            [str(AGENT), *args],
            cwd=self.repo,
            env=env,
            text=True,
            capture_output=True,
            timeout=20,
            check=True,
        )

    def test_validation_guard_rejects_early_final_until_check_passes(self):
        responder = SequenceResponder([
            tool_call("create", "create", {"path": "result.py", "content": "value = 1\n"}),
            completion("premature"),
            lambda payload: tool_call("validate", "bash", {"command": "python3 -m py_compile result.py"}),
            completion("implemented and validated"),
        ])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--fix", "create a minimal result module")
        reminder_payload = responder.payloads[2]
        self.assertIn("VALIDATION REQUIRED", reminder_payload["messages"][-1]["content"])
        self.assertEqual(result.stdout.strip(), "implemented and validated")
        self.assertTrue((self.repo / "result.py").is_file())

    def test_acceptance_guard_requires_explicit_test_change(self):
        responder = SequenceResponder([
            tool_call("create-app", "create", {"path": "app.py", "content": "VALUE = 1\n"}),
            tool_call("validate-app", "bash", {"command": "python3 -m py_compile app.py"}),
            completion("premature without test"),
            lambda payload: tool_call(
                "create-test",
                "create",
                {"path": "tests/test_app.py", "content": "import unittest\n\nclass Smoke(unittest.TestCase):\n    def test_value(self):\n        self.assertEqual(1, 1)\n"},
            ),
            tool_call("validate-test", "bash", {"command": "python3 -m unittest discover -s tests"}),
            completion("implementation and requested test complete"),
        ])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--implement", "add a test and minimal module")
        acceptance_payload = responder.payloads[3]
        self.assertIn("IMPLEMENTATION INCOMPLETE", acceptance_payload["messages"][-1]["content"])
        self.assertTrue((self.repo / "tests" / "test_app.py").is_file())
        self.assertEqual(result.stdout.strip(), "implementation and requested test complete")

    def test_debug_requires_reproduction_and_source_inspection(self):
        (self.repo / "config.py").write_text("timeout = None\n")
        responder = SequenceResponder([
            tool_call("reproduce", "bash", {"command": "python3 -c \"print('timeout=None')\""}),
            completion("runtime only"),
            lambda payload: tool_call("inspect", "inspect", {"paths": ["config.py"]}),
            completion("Reprodução: timeout=None\nCausa raiz: timeout is None\nEvidência: config.py\nPróxima ação: validate timeout"),
        ])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--debug", "trace the timeout failure")
        evidence_payload = responder.payloads[2]
        self.assertIn("DEBUG EVIDENCE REQUIRED", evidence_payload["messages"][-1]["content"])
        self.assertIn("Causa raiz", result.stdout)

    def test_review_evidence_gate_drops_unsupported_finding(self):
        draft = (
            "1. Severity: low\n"
            "   Evidence: optional policy may be ambiguous\n"
            "   Impact: could introduce ambiguity\n"
            "   Remediation: clarify it"
        )
        responder = SequenceResponder([completion(draft), completion("KEEP: NONE")])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--review", "review the supplied behavior")
        self.assertEqual(result.stdout.strip(), "Nenhum problema concreto encontrado no escopo revisado.")

    def test_security_evidence_gate_drops_unproven_finding(self):
        draft = (
            "1. Severity: high\n"
            "   Evidence: input might be untrusted\n"
            "   Impact: possible command injection\n"
            "   Remediation: validate input"
        )
        responder = SequenceResponder([completion(draft), completion("KEEP: NONE")])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--security", "review this hypothetical boundary")
        self.assertEqual(result.stdout.strip(), "Nenhum problema concreto encontrado no escopo revisado.")


if __name__ == "__main__":
    unittest.main()
