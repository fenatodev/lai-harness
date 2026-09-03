import importlib.util
from importlib.machinery import SourceFileLoader
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).parents[1] / "src" / "local-agent"
SPEC = importlib.util.spec_from_loader(
    "lai_local_agent",
    SourceFileLoader("lai_local_agent", str(SOURCE)),
)
agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent)


class LocalAgentTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        agent.ROOT = self.root.resolve()
        agent.read_paths.clear()

    def tearDown(self):
        self.temp.cleanup()

    def test_repository_confinement_blocks_parent_escape(self):
        with self.assertRaisesRegex(ValueError, "outside repository"):
            agent.safe_path("../private.txt")

    def test_repository_confinement_blocks_escaping_symlink(self):
        outside = self.root.parent / "outside-lai-test.txt"
        outside.write_text("private")
        try:
            (self.root / "escape").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "outside repository"):
                agent.safe_path("escape")
        finally:
            outside.unlink(missing_ok=True)

    def test_exact_edit_requires_unique_match(self):
        target = self.root / "sample.txt"
        target.write_text("old\nold\n")
        result = agent.tool_edit({"path": "sample.txt", "old": "old", "new": "new"})
        self.assertIn("occurs 2 times", result)
        self.assertEqual(target.read_text(), "old\nold\n")

    def test_batch_patch_is_prevalidated_before_writing(self):
        first = self.root / "first.txt"
        second = self.root / "second.txt"
        first.write_text("alpha")
        second.write_text("beta")
        result = agent.tool_patch({"changes": [
            {"path": "first.txt", "old": "alpha", "new": "changed"},
            {"path": "second.txt", "old": "missing", "new": "changed"},
        ]})
        self.assertTrue(result.startswith("ERROR: stale patch"))
        self.assertEqual(first.read_text(), "alpha")
        self.assertEqual(second.read_text(), "beta")

    def test_git_tool_exposes_only_read_operations(self):
        schema = next(item for item in agent.TOOLS if item["function"]["name"] == "git")
        operations = schema["function"]["parameters"]["properties"]["operation"]["enum"]
        self.assertEqual(operations, ["changes", "status", "diff", "diff-staged"])
        self.assertIn("unsupported", agent.tool_git({"operation": "commit"}))

    def test_bash_blocks_git_push(self):
        self.assertTrue(agent.tool_bash({"command": "git push origin main"}).startswith("BLOCKED:"))

    def test_metrics_and_audit_write_jsonl(self):
        agent.METRICS_DIR = self.root / "metrics"
        agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
        agent.AUDIT_DIR = self.root / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
        agent.METRICS_PRUNED = False
        agent.record_metric_event({"type": "smoke"})
        agent.record_audit_event({"type": "smoke"})
        self.assertEqual(json.loads(agent.METRICS_FILE.read_text())["type"], "smoke")
        self.assertEqual(json.loads(agent.AUDIT_FILE.read_text())["type"], "smoke")

    def test_api_key_file_is_configurable(self):
        key_file = self.root / "key"
        key_file.write_text("synthetic-test-key\n")
        with mock.patch.dict(os.environ, {"LAI_API_KEY_FILE": str(key_file)}):
            self.assertEqual(agent.llama_api_key(), "synthetic-test-key")

    def test_server_probe_uses_bearer_authentication(self):
        response = mock.MagicMock()
        response.status = 200
        response.__enter__.return_value = response
        with mock.patch.object(agent, "llama_api_key", return_value="synthetic-test-key"):
            with mock.patch.object(agent.urllib.request, "urlopen", return_value=response) as opened:
                self.assertTrue(agent.server_ready("127.0.0.1"))
        request = opened.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer synthetic-test-key")

    @unittest.skipUnless(__import__("shutil").which("node"), "node is not installed")
    def test_post_patch_sanity_catches_newerror_regression(self):
        target = self.root / "sample.js"
        target.write_text("function run() { return 1; }\n")
        subprocess.run(["git", "add", "sample.js"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "base"],
            cwd=self.root,
            check=True,
        )
        target.write_text("function run() { throw newError('failed'); }\n")
        result = agent.post_patch_sanity("unused", "fix regression", ["sample.js"])
        self.assertIsNotNone(result)
        self.assertIn("newError", result)

    def test_guard_contracts_remain_present(self):
        source = SOURCE.read_text()
        self.assertIn("needs_validation", source)
        self.assertIn("task_explicitly_requires_test_change", source)
        self.assertIn("debug_source_inspected", source)
        self.assertIn("POST_PATCH_SANITY", source)


if __name__ == "__main__":
    unittest.main()
