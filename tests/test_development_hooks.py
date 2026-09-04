import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).parents[1]
GATE_PATH = ROOT / ".cursor" / "hooks" / "guard_shell.py"
FEEDBACK_PATH = ROOT / ".cursor" / "hooks" / "feedback_check.py"


def load_script(name, path):
    spec = importlib.util.spec_from_loader(name, SourceFileLoader(name, str(path)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DevelopmentHooksTest(unittest.TestCase):
    def run_gate(self, payload):
        raw = payload if isinstance(payload, str) else json.dumps(payload)
        result = subprocess.run(
            [sys.executable, str(GATE_PATH)],
            cwd=ROOT,
            input=raw,
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_shell_gate_maps_policy_allow_ask_and_deny(self):
        self.assertEqual(
            self.run_gate({"command": "git status --short"})["permission"],
            "allow",
        )
        self.assertEqual(
            self.run_gate({"command": "git commit -m test"})["permission"],
            "ask",
        )
        self.assertEqual(
            self.run_gate({"command": "npm publish"})["permission"],
            "deny",
        )

    def test_shell_gate_fails_closed_for_malformed_payload(self):
        payload = self.run_gate("{bad json")
        self.assertEqual(payload["permission"], "ask")
        self.assertIn("failed closed", payload["userMessage"])

    def test_shell_gate_fails_closed_when_policy_check_is_unavailable(self):
        gate = load_script("lai_guard_shell_test", GATE_PATH)
        stdout = io.StringIO()
        with mock.patch.object(gate, "classify", side_effect=RuntimeError("offline")), mock.patch.object(
            gate.sys, "stdin", io.StringIO('{"command":"echo ok"}')
        ), mock.patch.object(gate.sys, "stdout", stdout):
            gate.main()
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["permission"], "ask")
        self.assertIn("failed closed", payload["userMessage"])

    def test_feedback_path_is_repository_confined(self):
        feedback = load_script("lai_feedback_test", FEEDBACK_PATH)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            inside = root / "sample.py"
            inside.write_text("print('ok')\n")
            outside = root.parent / "outside-hook-test.py"
            outside.write_text("print('outside')\n")
            old_root = feedback.ROOT
            try:
                feedback.ROOT = root
                self.assertEqual(feedback.edited_path({"file_path": "sample.py"}), inside)
                self.assertIsNone(feedback.edited_path({"file_path": str(outside)}))
                commands = feedback.feedback_commands(inside)
                self.assertTrue(any("py_compile" in item for cmd in commands for item in cmd))
            finally:
                feedback.ROOT = old_root
                outside.unlink(missing_ok=True)

    def test_feedback_hook_is_best_effort_and_non_blocking(self):
        result = subprocess.run(
            [sys.executable, str(FEEDBACK_PATH)],
            cwd=ROOT,
            input=json.dumps({"file_path": "not-a-supported-file.txt"}),
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(json.loads(result.stdout), {})


if __name__ == "__main__":
    unittest.main()
