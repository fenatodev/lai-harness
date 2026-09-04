import json
import hashlib
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


def truncated_completion(content="partial response", tokens=640):
    return {
        "choices": [{
            "finish_reason": "length",
            "message": {
                "role": "assistant",
                "content": content,
            },
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": tokens,
            "total_tokens": 10 + tokens,
        },
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
        subprocess.run(["git", "branch", "-M", "main"], cwd=self.repo, check=True)

    def tearDown(self):
        self.temp.cleanup()

    def run_agent(self, server, *args, check=True, allow_protected_writes=True):
        env = {
            **os.environ,
            "LAI_HOST": server.host,
            "LAI_PORT": str(server.port),
            "LAI_API_KEY_FILE": str(self.key),
            "LAI_DATA_DIR": str(self.data),
            "LAI_MODEL": "fake-local-model",
        }
        if allow_protected_writes:
            env["LAI_ALLOW_PROTECTED_BRANCH_WRITES"] = "1"
        else:
            env.pop("LAI_ALLOW_PROTECTED_BRANCH_WRITES", None)
        return subprocess.run(
            [str(AGENT), *args],
            cwd=self.repo,
            env=env,
            text=True,
            capture_output=True,
            timeout=20,
            check=check,
        )

    def test_protected_branch_write_guard_blocks_main_without_override(self):
        responder = SequenceResponder([
            tool_call(
                "create",
                "create",
                {"path": "blocked.py", "content": "VALUE = 1\n"},
            ),
            completion("blocked by protected branch guard"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--implement",
                "create blocked.py",
                allow_protected_writes=False,
            )

        self.assertEqual(result.returncode, 0)
        self.assertFalse((self.repo / "blocked.py").exists())
        self.assertEqual(result.stdout.strip(), "blocked by protected branch guard")
        self.assertIn(
            "protected branch main",
            responder.payloads[1]["messages"][-1]["content"],
        )

    def test_policy_ask_stops_run_and_records_user_action_outcome(self):
        responder = SequenceResponder([
            tool_call(
                "commit",
                "bash",
                {"command": "git commit -m synthetic"},
            ),
        ])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--fix",
                "commit the current work",
            )

        self.assertTrue(result.stdout.strip().startswith("POLICY ASK:"))
        self.assertEqual(len(responder.payloads), 1)
        events = [
            json.loads(line)
            for line in (self.data / "audit" / "events.jsonl").read_text().splitlines()
        ]
        policy = [event for event in events if event.get("type") == "policy_decision"]
        outcomes = [event for event in events if event.get("type") == "run_outcome"]
        self.assertEqual(policy[-1]["decision"], "ASK")
        self.assertEqual(outcomes[-1]["outcome"], "user_action_required")
        self.assertEqual(outcomes[-1]["tool"], "bash")

    def test_explicit_resume_starts_fresh_run_without_tool_replay(self):
        branch = subprocess.run(
            ["git", "branch", "--show-current"], cwd=self.repo,
            text=True, capture_output=True, check=True,
        ).stdout.strip() or "[detached HEAD]"
        status = subprocess.run(
            ["git", "status", "--short"], cwd=self.repo,
            text=True, capture_output=True, check=True,
        ).stdout.strip() or "[clean]"
        key = hashlib.sha256(str(self.repo.resolve()).encode("utf-8")).hexdigest()[:16]
        checkpoint_dir = self.data / "checkpoints"
        checkpoint_dir.mkdir(parents=True)
        checkpoint = {
            "schema_version": 1,
            "root": str(self.repo.resolve()),
            "run_id": "prior-run",
            "resumed_from": None,
            "mode": "general",
            "task": "resume synthetic task",
            "phase": "tool_completed",
            "terminal": False,
            "branch": branch,
            "git_status": status,
            "tracked_hashes": {},
            "last_tool": "read",
            "reason": None,
            "updated_at": "2026-01-01T00:00:00Z",
        }
        checkpoint_path = checkpoint_dir / f"{key}.json"
        checkpoint_path.write_text(json.dumps(checkpoint))

        responder = SequenceResponder([completion("resumed safely")])
        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(server, "--resume")

        self.assertEqual(result.stdout.strip(), "resumed safely")
        self.assertEqual(len(responder.payloads), 1)
        system = responder.payloads[0]["messages"][0]["content"]
        self.assertIn("RECOVERY CONTEXT", system)
        self.assertIn("Previous run: prior-run", system)
        self.assertIn("Do not assume any previous tool call should be replayed", system)
        events = [
            json.loads(line)
            for line in (self.data / "audit" / "events.jsonl").read_text().splitlines()
        ]
        resume = [event for event in events if event.get("type") == "recovery_resume"][-1]
        self.assertEqual(resume["from_run_id"], "prior-run")
        self.assertNotEqual(resume["run_id"], "prior-run")
        final_checkpoint = json.loads(checkpoint_path.read_text())
        self.assertEqual(final_checkpoint["phase"], "completed")
        self.assertTrue(final_checkpoint["terminal"])
        self.assertEqual(final_checkpoint["resumed_from"], "prior-run")
        self.assertNotEqual(final_checkpoint["run_id"], "prior-run")

    def test_truncated_response_is_discarded_and_retried_once(self):
        partial = "PARTIAL_OUTPUT_MUST_NOT_ENTER_HISTORY"

        responder = SequenceResponder([
            truncated_completion(partial, tokens=640),
            tool_call(
                "create",
                "create",
                {
                    "path": "result.py",
                    "content": "value = 1\n",
                },
            ),
            tool_call(
                "validate",
                "bash",
                {
                    "command": "python3 -m py_compile result.py",
                },
            ),
            completion("implemented after truncation recovery"),
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
            "implemented after truncation recovery",
        )
        self.assertTrue((self.repo / "result.py").is_file())

        self.assertEqual(
            responder.payloads[0]["max_tokens"],
            640,
        )
        self.assertEqual(
            responder.payloads[1]["max_tokens"],
            1280,
        )

        retry_messages = responder.payloads[1]["messages"]

        self.assertFalse(any(
            partial in str(message.get("content", ""))
            for message in retry_messages
        ))

        self.assertIn(
            "RESPONSE TRUNCATED",
            retry_messages[-1]["content"],
        )

    def test_plan_early_completion_is_forced_through_finalizer(self):
        draft = "DRAFT_PLAN_MUST_NOT_BE_RETURNED"

        responder = SequenceResponder([
            completion(draft),
            completion("Goal: finalized plan"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--plan",
                "Produce a concise implementation plan.",
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.strip(),
            "Goal: finalized plan",
        )
        self.assertNotIn(draft, result.stdout)

        self.assertEqual(
            [payload["max_tokens"] for payload in responder.payloads],
            [256, 1536],
        )

        final_payload = responder.payloads[1]

        self.assertFalse(final_payload.get("tools"))
        self.assertIn(
            "[project snapshot]",
            final_payload["messages"][-1]["content"],
        )
        self.assertNotIn(
            draft,
            str(final_payload["messages"]),
        )

    def test_plan_final_synthesis_retries_truncation(self):
        partial = "PARTIAL_PLAN_MUST_NOT_BE_RETURNED"

        responder = SequenceResponder([
            tool_call(
                "search-one",
                "search",
                {"query": "first"},
            ),
            tool_call(
                "search-two",
                "search",
                {"query": "second"},
            ),
            truncated_completion(partial, tokens=1536),
            completion("complete final plan"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--plan",
                "Inspect the repository and produce a concise plan.",
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "complete final plan")
        self.assertNotIn(partial, result.stdout)

        self.assertEqual(
            [payload["max_tokens"] for payload in responder.payloads],
            [256, 256, 1536, 3072],
        )

        metric_events = [
            json.loads(line)
            for line in (
                self.data / "metrics" / "events.jsonl"
            ).read_text().splitlines()
        ]

        truncations = [
            event
            for event in metric_events
            if (
                event.get("type") == "agent_limit"
                and event.get("reason") == "response_truncated"
            )
        ]

        self.assertEqual(len(truncations), 1)
        self.assertTrue(truncations[0]["retry"])
        self.assertEqual(truncations[0]["max_tokens"], 1536)
        self.assertEqual(truncations[0]["retry_max_tokens"], 3072)

    def test_plan_final_synthesis_second_truncation_fails_cleanly(self):
        first_partial = "FIRST_PARTIAL_PLAN"
        second_partial = "SECOND_PARTIAL_PLAN"

        responder = SequenceResponder([
            tool_call(
                "search-one",
                "search",
                {"query": "first"},
            ),
            tool_call(
                "search-two",
                "search",
                {"query": "second"},
            ),
            truncated_completion(first_partial, tokens=1536),
            truncated_completion(second_partial, tokens=3072),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--plan",
                "Inspect the repository and produce a concise plan.",
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "plan synthesis truncated twice",
            result.stderr,
        )
        self.assertNotIn(first_partial, result.stdout)
        self.assertNotIn(second_partial, result.stdout)

        self.assertEqual(
            [payload["max_tokens"] for payload in responder.payloads],
            [256, 256, 1536, 3072],
        )

        metric_events = [
            json.loads(line)
            for line in (
                self.data / "metrics" / "events.jsonl"
            ).read_text().splitlines()
        ]

        truncations = [
            event
            for event in metric_events
            if (
                event.get("type") == "agent_limit"
                and event.get("reason") == "response_truncated"
            )
        ]

        self.assertEqual(len(truncations), 2)
        self.assertTrue(truncations[0]["retry"])
        self.assertFalse(truncations[1]["retry"])

    def test_separate_rounds_each_get_one_truncation_retry(self):
        responder = SequenceResponder([
            truncated_completion("partial create", tokens=640),
            tool_call(
                "create",
                "create",
                {
                    "path": "result.py",
                    "content": "value = 1\n",
                },
            ),
            truncated_completion("partial validation", tokens=640),
            tool_call(
                "validate",
                "bash",
                {
                    "command": "python3 -m py_compile result.py",
                },
            ),
            completion("implemented after two recovered rounds"),
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
            "implemented after two recovered rounds",
        )

        self.assertEqual(
            [payload["max_tokens"] for payload in responder.payloads],
            [640, 1280, 640, 1280, 640],
        )

    def test_forced_write_phase_gets_larger_token_budget(self):
        calls = [
            tool_call(
                f"search-{index}",
                "search",
                {"query": f"needle-{index}"},
            )
            for index in range(6)
        ]

        def assert_write_budget(payload):
            self.assertEqual(payload["max_tokens"], 2048)

            offered = {
                tool["function"]["name"]
                for tool in payload.get("tools", [])
            }
            self.assertEqual(offered, {"patch", "create", "rewrite"})

            return tool_call(
                "create",
                "create",
                {
                    "path": "result.py",
                    "content": "value = 1\n",
                },
            )

        responder = SequenceResponder([
            *calls,
            assert_write_budget,
            tool_call(
                "validate",
                "bash",
                {
                    "command": "python3 -m py_compile result.py",
                },
            ),
            completion("implemented with write-phase budget"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--implement",
                "Find the target and create result.py with value = 1.",
            )

        self.assertEqual(result.returncode, 0)
        self.assertTrue((self.repo / "result.py").is_file())
        self.assertEqual(
            result.stdout.strip(),
            "implemented with write-phase budget",
        )

    def test_forced_write_phase_truncation_retries_at_4096(self):
        calls = [
            tool_call(
                f"search-{index}",
                "search",
                {"query": f"needle-{index}"},
            )
            for index in range(6)
        ]

        responder = SequenceResponder([
            *calls,
            truncated_completion("partial write", tokens=2048),
            tool_call(
                "create",
                "create",
                {
                    "path": "result.py",
                    "content": "value = 1\n",
                },
            ),
            tool_call(
                "validate",
                "bash",
                {
                    "command": "python3 -m py_compile result.py",
                },
            ),
            completion("implemented after large retry"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--implement",
                "Find the target and create result.py with value = 1.",
            )

        self.assertEqual(result.returncode, 0)

        self.assertEqual(
            responder.payloads[6]["max_tokens"],
            2048,
        )
        self.assertEqual(
            responder.payloads[7]["max_tokens"],
            4096,
        )

    def test_second_truncation_fails_cleanly(self):
        responder = SequenceResponder([
            truncated_completion("first partial", tokens=640),
            truncated_completion("second partial", tokens=1280),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--implement",
                "Create result.py with value = 1.",
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "model response truncated twice",
            result.stderr,
        )
        self.assertFalse((self.repo / "result.py").exists())

        metric_events = [
            json.loads(line)
            for line in (
                self.data / "metrics" / "events.jsonl"
            ).read_text().splitlines()
        ]

        truncations = [
            event
            for event in metric_events
            if (
                event.get("type") == "agent_limit"
                and event.get("reason") == "response_truncated"
            )
        ]

        self.assertEqual(len(truncations), 2)
        self.assertTrue(truncations[0]["retry"])
        self.assertFalse(truncations[1]["retry"])
        self.assertEqual(truncations[0]["max_tokens"], 640)
        self.assertEqual(
            truncations[0]["retry_max_tokens"],
            1280,
        )
        self.assertEqual(truncations[1]["max_tokens"], 1280)

    def test_assertion_failure_blocks_test_weakening_until_source_repair(self):
        responder = SequenceResponder([
            tool_call(
                "create-app",
                "create",
                {
                    "path": "app.py",
                    "content": "VALUE = 500\n",
                },
            ),
            tool_call(
                "create-test",
                "create",
                {
                    "path": "tests/test_app.py",
                    "content": (
                        "import unittest\n"
                        "from app import VALUE\n\n"
                        "class AppTest(unittest.TestCase):\n"
                        "    def test_value(self):\n"
                        "        self.assertEqual(VALUE, 2)\n"
                    ),
                },
            ),
            tool_call(
                "validate-fail",
                "bash",
                {
                    "command": (
                        "python3 -m unittest discover "
                        "-s tests -v"
                    ),
                },
            ),
            tool_call(
                "weaken-test",
                "patch",
                {
                    "changes": [
                        {
                            "path": "tests/test_app.py",
                            "old": (
                                "self.assertEqual(VALUE, 2)"
                            ),
                            "new": (
                                "self.assertLessEqual(VALUE, 5)"
                            ),
                        },
                    ],
                },
            ),
            tool_call(
                "fix-source",
                "patch",
                {
                    "changes": [
                        {
                            "path": "app.py",
                            "old": "VALUE = 500",
                            "new": "VALUE = 2",
                        },
                    ],
                },
            ),
            tool_call(
                "validate-pass",
                "bash",
                {
                    "command": (
                        "python3 -m unittest discover "
                        "-s tests -v"
                    ),
                },
            ),
            completion("source repaired and validated"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--implement",
                "Create app.py and tests/test_app.py so the test passes.",
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            (self.repo / "app.py").read_text(),
            "VALUE = 2\n",
        )

        test_text = (
            self.repo
            / "tests"
            / "test_app.py"
        ).read_text()

        self.assertIn(
            "self.assertEqual(VALUE, 2)",
            test_text,
        )
        self.assertNotIn(
            "assertLessEqual",
            test_text,
        )

        repair_payload = responder.payloads[4]

        self.assertIn(
            "VALIDATION FAILURE GUARD",
            str(repair_payload["messages"]),
        )

        audit_events = [
            json.loads(line)
            for line in (
                self.data
                / "audit"
                / "events.jsonl"
            ).read_text().splitlines()
        ]

        guarded = [
            event
            for event in audit_events
            if event.get("type") == "validation_guard"
        ]

        self.assertEqual(
            guarded[-1]["reason"],
            "test_write_after_assertion_failure",
        )

    def test_assertion_guard_allows_test_correction_after_source_revalidation(self):
        responder = SequenceResponder([
            tool_call(
                "create-app",
                "create",
                {
                    "path": "app.py",
                    "content": "VALUE = 500\n",
                },
            ),
            tool_call(
                "create-test",
                "create",
                {
                    "path": "tests/test_app.py",
                    "content": (
                        "import unittest\n"
                        "from app import VALUE\n\n"
                        "class AppTest(unittest.TestCase):\n"
                        "    def test_value(self):\n"
                        "        self.assertEqual(VALUE, 200)\n"
                    ),
                },
            ),
            tool_call(
                "validate-initial-failure",
                "bash",
                {
                    "command": (
                        "python3 -m unittest discover "
                        "-s tests -v"
                    ),
                },
            ),
            tool_call(
                "repair-source",
                "patch",
                {
                    "changes": [
                        {
                            "path": "app.py",
                            "old": "VALUE = 500",
                            "new": "VALUE = 3",
                        },
                    ],
                },
            ),
            tool_call(
                "revalidate-source",
                "bash",
                {
                    "command": (
                        "python3 -m unittest discover "
                        "-s tests -v"
                    ),
                },
            ),
            tool_call(
                "correct-test",
                "patch",
                {
                    "changes": [
                        {
                            "path": "tests/test_app.py",
                            "old": (
                                "self.assertEqual(VALUE, 200)"
                            ),
                            "new": (
                                "self.assertEqual(VALUE, 3)"
                            ),
                        },
                    ],
                },
            ),
            tool_call(
                "validate-final",
                "bash",
                {
                    "command": (
                        "python3 -m unittest discover "
                        "-s tests -v"
                    ),
                },
            ),
            completion("source-first repair and test correction validated"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--implement",
                (
                    "Create app.py with VALUE = 3 and add a test "
                    "that verifies that requirement."
                ),
            )

        self.assertEqual(result.returncode, 0)

        self.assertEqual(
            (self.repo / "app.py").read_text(),
            "VALUE = 3\n",
        )

        self.assertIn(
            "self.assertEqual(VALUE, 3)",
            (
                self.repo
                / "tests"
                / "test_app.py"
            ).read_text(),
        )

        audit_events = [
            json.loads(line)
            for line in (
                self.data
                / "audit"
                / "events.jsonl"
            ).read_text().splitlines()
        ]

        guarded = [
            event
            for event in audit_events
            if event.get("type") == "validation_guard"
        ]

        self.assertEqual(
            guarded,
            [],
        )

    def test_validation_failure_allows_test_syntax_repair(self):
        responder = SequenceResponder([
            tool_call(
                "create-app",
                "create",
                {
                    "path": "app.py",
                    "content": "VALUE = 1\n",
                },
            ),
            tool_call(
                "create-test",
                "create",
                {
                    "path": "tests/test_app.py",
                    "content": (
                        "import unittest\n"
                        "from app import VALUE\n\n"
                        "class AppTest(unittest.TestCase):\n"
                        "    def test_value(self)\n"
                        "        self.assertEqual(VALUE, 1)\n"
                    ),
                },
            ),
            tool_call(
                "validate-fail",
                "bash",
                {
                    "command": (
                        "python3 -m unittest discover "
                        "-s tests -v"
                    ),
                },
            ),
            tool_call(
                "fix-test-syntax",
                "patch",
                {
                    "changes": [
                        {
                            "path": "tests/test_app.py",
                            "old": "def test_value(self)\n",
                            "new": "def test_value(self):\n",
                        },
                    ],
                },
            ),
            tool_call(
                "validate-pass",
                "bash",
                {
                    "command": (
                        "python3 -m unittest discover "
                        "-s tests -v"
                    ),
                },
            ),
            completion("test syntax repaired"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--implement",
                "Create app.py and tests/test_app.py and make validation pass.",
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "def test_value(self):",
            (
                self.repo
                / "tests"
                / "test_app.py"
            ).read_text(),
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
        self.assertEqual(offered, {"patch", "create", "rewrite"})
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

    def test_post_write_phase_forces_validation_before_exploration(self):
        target = self.repo / "result.py"
        target.write_text("value = 0\n")

        responder = SequenceResponder([
            tool_call(
                "read",
                "read",
                {"path": "result.py"},
            ),
            tool_call(
                "edit",
                "edit",
                {
                    "path": "result.py",
                    "old": "value = 0",
                    "new": "value = 1",
                },
            ),
            tool_call(
                "wander",
                "search",
                {"query": "value"},
            ),
            tool_call(
                "validate",
                "bash",
                {
                    "command": (
                        "python3 -m py_compile result.py"
                    ),
                },
            ),
            completion("implemented and validated"),
        ])

        with FakeLlamaServer(responder=responder) as server:
            result = self.run_agent(
                server,
                "--fix",
                "Change result.py value from 0 to 1 and validate it.",
            )

        self.assertEqual(
            target.read_text(),
            "value = 1\n",
        )

        post_write_tools = {
            tool["function"]["name"]
            for tool in responder.payloads[2].get("tools", [])
        }
        self.assertEqual(post_write_tools, {"bash"})

        blocked_messages = responder.payloads[3]["messages"]
        self.assertTrue(any(
            (
                "BLOCKED: post-write progress phase=validate"
                in str(message.get("content", ""))
            )
            for message in blocked_messages
        ))

        self.assertEqual(
            responder.payloads[-1].get("tools", []),
            [],
        )

        self.assertEqual(
            result.stdout.strip(),
            "implemented and validated",
        )

        metric_events = [
            json.loads(line)
            for line in (
                self.data / "metrics" / "events.jsonl"
            ).read_text().splitlines()
        ]

        blocked = [
            event
            for event in metric_events
            if (
                event.get("type") == "progress_guard"
                and event.get("reason")
                == "post_write_tool_blocked"
            )
        ]

        self.assertEqual(len(blocked), 1)
        self.assertEqual(blocked[0]["phase"], "validate")
        self.assertEqual(blocked[0]["tool_name"], "search")

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
        key = hashlib.sha256(str(self.repo.resolve()).encode("utf-8")).hexdigest()[:16]
        checkpoint = json.loads(
            (self.data / "checkpoints" / f"{key}.json").read_text()
        )
        self.assertEqual(checkpoint["phase"], "failed")
        self.assertTrue(checkpoint["terminal"])

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
        audit_events = [
            json.loads(line)
            for line in (self.data / "audit" / "events.jsonl").read_text().splitlines()
        ]
        phases = [
            event.get("phase")
            for event in audit_events
            if event.get("type") == "checkpoint"
        ]
        self.assertIn("started", phases)
        self.assertIn("tool_completed", phases)
        self.assertIn("validation_completed", phases)
        self.assertEqual(phases[-1], "completed")

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
