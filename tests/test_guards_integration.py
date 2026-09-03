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

    def run_agent(self, server, *args, check=True):
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
            check=check,
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

    def test_explicit_user_validation_command_can_finish_write_flow(self):
        responder = SequenceResponder([
            tool_call(
                "create",
                "create",
                {
                    "path": "hello.txt",
                    "content": "hello alpha3\n",
                },
            ),
            tool_call(
                "verify",
                "bash",
                {"command": "cat hello.txt"},
            ),
            completion("implemented and verified"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--implement",
                (
                    "Crie somente hello.txt com o texto hello alpha3. "
                    "Não crie outros arquivos. "
                    "Depois valide apenas com: cat hello.txt"
                ),
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip(),
            "implemented and verified",
        )
        self.assertEqual(
            (self.repo / "hello.txt").read_text(),
            "hello alpha3\n",
        )

        final_messages = responder.payloads[-1]["messages"]
        self.assertFalse(any(
            "VALIDATION REQUIRED" in str(message.get("content", ""))
            for message in final_messages
        ))

    def test_unrequested_cat_does_not_bypass_validation_guard(self):
        responder = SequenceResponder([
            tool_call(
                "create",
                "create",
                {
                    "path": "result.py",
                    "content": "value = 1\n",
                },
            ),
            tool_call(
                "cat",
                "bash",
                {"command": "cat result.py"},
            ),
            completion("premature"),
            tool_call(
                "validate",
                "bash",
                {"command": "python3 -m py_compile result.py"},
            ),
            completion("implemented and validated"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--implement",
                "Create result.py with value = 1.",
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip(),
            "implemented and validated",
        )

        validation_prompt = responder.payloads[3]["messages"]

        self.assertTrue(any(
            "VALIDATION REQUIRED" in str(message.get("content", ""))
            for message in validation_prompt
        ))

    def test_repeated_exploration_is_blocked_and_forces_write_phase(self):
        repeated = {"paths": ["missing.py"]}
        responder = SequenceResponder([
            tool_call("inspect-1", "inspect", repeated),
            tool_call("inspect-2", "inspect", repeated),
            completion("implemented successfully"),
            completion("IMPLEMENTATION_IMPOSSIBLE:"),
            completion("IMPLEMENTATION_IMPOSSIBLE:   "),
            completion("IMPLEMENTATION_IMPOSSIBLE: the target file is absent."),
        ])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--implement", "change missing.py")

        self.assertEqual(result.stderr.count("\n[inspect] "), 1)
        self.assertIn(
            "BLOCKED: pre-write exploration budget exhausted",
            responder.payloads[2]["messages"][-2]["content"],
        )
        self.assertIn(
            "PRE-WRITE EXPLORATION ENDED",
            responder.payloads[2]["messages"][-1]["content"],
        )
        offered = {
            tool["function"]["name"]
            for tool in responder.payloads[2].get("tools", [])
        }
        self.assertEqual(offered, {"patch", "create"})
        self.assertIn(
            "PHASE-SHIFT RESPONSE REJECTED",
            responder.payloads[3]["messages"][-1]["content"],
        )
        self.assertIn(
            "PHASE-SHIFT RESPONSE REJECTED",
            responder.payloads[4]["messages"][-1]["content"],
        )
        self.assertIn(
            "PHASE-SHIFT RESPONSE REJECTED",
            responder.payloads[5]["messages"][-1]["content"],
        )
        self.assertEqual(
            result.stdout.strip(),
            "IMPLEMENTATION_IMPOSSIBLE: the target file is absent.",
        )

    def test_distinct_read_only_calls_work_within_budget(self):
        (self.repo / "one.py").write_text("ONE = 1\n")
        (self.repo / "two.py").write_text("TWO = 2\n")
        responder = SequenceResponder([
            tool_call("inspect-1", "inspect", {"paths": ["one.py"]}),
            tool_call("inspect-2", "inspect", {"paths": ["two.py"]}),
            completion("No change is needed."),
        ])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--implement", "inspect both files")

        self.assertEqual(result.stderr.count("\n[inspect] "), 2)
        self.assertNotIn("PRE-WRITE EXPLORATION ENDED", str(responder.payloads))

    def test_validation_bash_remains_available_after_successful_write(self):
        responder = SequenceResponder([
            tool_call("inspect", "inspect", {"paths": ["AGENTS.md"]}),
            tool_call(
                "create",
                "create",
                {"path": "result.py", "content": "value = 1\n"},
            ),
            tool_call(
                "validate",
                "bash",
                {"command": "python3 -m py_compile result.py"},
            ),
            completion("implemented and validated"),
        ])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--implement", "create result.py")

        self.assertIn("exit_code=0", responder.payloads[3]["messages"][-1]["content"])
        self.assertEqual(result.stdout.strip(), "implemented and validated")

    def test_budget_exhaustion_records_specific_metric_and_audit_event(self):
        calls = [
            tool_call(f"search-{index}", "search", {"query": f"needle-{index}"})
            for index in range(6)
        ]
        responder = SequenceResponder([
            *calls,
            completion(
                "IMPLEMENTATION_IMPOSSIBLE: no target was found in the collected evidence."
            ),
        ])
        with FakeLlamaServer(responder=responder) as server:
            self.run_agent(server, "--implement", "find a target and change it")

        metric_events = [
            json.loads(line)
            for line in (self.data / "metrics" / "events.jsonl").read_text().splitlines()
        ]
        audit_events = [
            json.loads(line)
            for line in (self.data / "audit" / "events.jsonl").read_text().splitlines()
        ]
        for events in (metric_events, audit_events):
            limits = [event for event in events if event.get("type") == "agent_limit"]
            self.assertEqual(limits[-1]["reason"], "exploration_budget_exhausted")
            self.assertEqual(limits[-1]["trigger"], "budget_reached")
            self.assertEqual(limits[-1]["exploration_calls"], 6)
            self.assertNotIn("signature", limits[-1])
            self.assertRegex(limits[-1]["signature_hash"], r"^[0-9a-f]{64}$")

        outcomes = [
            event
            for event in metric_events
            if event.get("type") == "run_outcome"
        ]
        self.assertEqual(outcomes[-1]["outcome"], "implementation_impossible")

    def test_overall_round_limit_has_a_distinct_reason(self):
        responder = SequenceResponder([
            tool_call(
                f"search-{index}",
                "search",
                {"query": "same-query"},
            )
            for index in range(12)
        ])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--fix",
                "change an unknown target",
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("overall round limit reached (12 rounds)", result.stderr)
        events = [
            json.loads(line)
            for line in (self.data / "metrics" / "events.jsonl").read_text().splitlines()
            if json.loads(line).get("type") == "agent_limit"
        ]
        self.assertEqual(events[0]["reason"], "exploration_budget_exhausted")
        self.assertEqual(events[-1]["reason"], "overall_round_limit_reached")

    def test_simple_implement_still_creates_and_validates(self):
        responder = SequenceResponder([
            tool_call(
                "create",
                "create",
                {"path": "simple.py", "content": "VALUE = 1\n"},
            ),
            tool_call(
                "validate",
                "bash",
                {"command": "python3 -m py_compile simple.py"},
            ),
            completion("done"),
        ])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--implement", "create simple.py")

        self.assertEqual(result.stdout.strip(), "done")
        self.assertEqual((self.repo / "simple.py").read_text(), "VALUE = 1\n")

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
