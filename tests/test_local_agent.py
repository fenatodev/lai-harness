import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout


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
        agent.STATE_BASE = self.root / ".lai-data" / "state"
        agent.CONFIG["api_key_file"] = self.root / "key"
        agent.read_paths.clear()

    def tearDown(self):
        self.temp.cleanup()

    def test_repository_confinement_blocks_parent_escape(self):
        with self.assertRaisesRegex(ValueError, "outside repository"):
            agent.safe_path("../private.txt")

    def test_read_returns_a_bounded_chunk_and_tracks_path(self):
        (self.root / "sample.txt").write_text("one\ntwo\nthree\n")
        result = agent.tool_read({"path": "sample.txt", "start_line": 2, "max_lines": 1})
        self.assertIn("lines 2-2 of 3", result)
        self.assertTrue(result.endswith("two"))
        self.assertIn("sample.txt", agent.read_paths)

    def test_search_finds_text_inside_repository(self):
        (self.root / "sample.txt").write_text("needle here\n")
        result = agent.tool_search({"path": ".", "query": "needle"})
        self.assertIn("sample.txt:1:needle here", result)

    def test_inspect_batches_known_files(self):
        (self.root / "first.txt").write_text("alpha\n")
        (self.root / "second.txt").write_text("beta\n")
        result = agent.tool_inspect({"paths": ["first.txt", "second.txt"]})
        self.assertIn("===== first.txt =====", result)
        self.assertIn("===== second.txt =====", result)
        self.assertIn("alpha", result)
        self.assertIn("beta", result)

    def test_create_refuses_overwrite(self):
        first = agent.tool_create({"path": "new/file.txt", "content": "created"})
        second = agent.tool_create({"path": "new/file.txt", "content": "replaced"})
        self.assertTrue(first.startswith("OK:"))
        self.assertIn("already exists", second)
        self.assertEqual((self.root / "new/file.txt").read_text(), "created")

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

    def test_batch_patch_applies_and_retry_is_stale_safe(self):
        first = self.root / "first.txt"
        second = self.root / "second.txt"
        first.write_text("alpha")
        second.write_text("beta")
        changes = [
            {"path": "first.txt", "old": "alpha", "new": "one"},
            {"path": "second.txt", "old": "beta", "new": "two"},
        ]
        self.assertIn("applied=2", agent.tool_patch({"changes": changes}))
        self.assertIn("already_applied=2", agent.tool_patch({"changes": changes}))
        self.assertEqual(first.read_text(), "one")
        self.assertEqual(second.read_text(), "two")

    def test_batch_patch_refuses_symlink_even_inside_repository(self):
        target = self.root / "target.txt"
        target.write_text("alpha")
        (self.root / "link.txt").symlink_to(target)
        result = agent.tool_patch({"changes": [
            {"path": "link.txt", "old": "alpha", "new": "changed"},
        ]})
        self.assertIn("refuses symlink", result)
        self.assertEqual(target.read_text(), "alpha")

    def test_git_tool_exposes_only_read_operations(self):
        schema = next(item for item in agent.TOOLS if item["function"]["name"] == "git")
        operations = schema["function"]["parameters"]["properties"]["operation"]["enum"]
        self.assertEqual(operations, ["changes", "status", "diff", "diff-staged"])
        self.assertIn("unsupported", agent.tool_git({"operation": "commit"}))

    def test_git_tool_reports_status_and_diff_without_mutation(self):
        target = self.root / "tracked.txt"
        target.write_text("before\n")
        subprocess.run(["git", "add", "tracked.txt"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "base"],
            cwd=self.root,
            check=True,
        )
        target.write_text("after\n")
        self.assertIn("tracked.txt", agent.tool_git({"operation": "status"}))
        diff = agent.tool_git({"operation": "diff", "path": "tracked.txt"})
        self.assertIn("-before", diff)
        self.assertIn("+after", diff)
        self.assertEqual(target.read_text(), "after\n")

    def test_bash_denylist_blocks_known_dangerous_commands(self):
        commands = [
            "sudo true",
            "pip install package",
            "rm -rf generated",
            "git reset --hard HEAD",
            "git push origin main",
            "docker compose down",
            "TRUNCATE TABLE records",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assertTrue(agent.tool_bash({"command": command}).startswith("BLOCKED:"))

    def test_bash_blocks_git_mutation_subcommands(self):
        subcommands = [
            "add", "commit", "am", "merge", "rebase", "cherry-pick",
            "revert", "tag", "push", "pull", "reset", "clean",
            "checkout", "switch", "restore", "rm", "mv", "init", "clone",
            "update-ref", "symbolic-ref", "fetch",
        ]
        for subcommand in subcommands:
            with self.subTest(subcommand=subcommand):
                result = agent.tool_bash({"command": f"git {subcommand} synthetic-target"})
                self.assertTrue(result.startswith("BLOCKED:"), result)
                self.assertIn(f"git {subcommand}", result)

    def test_bash_blocks_git_mutation_with_global_options_paths_and_chains(self):
        git_path = __import__("shutil").which("git")
        commands = [
            f"git -C {self.root} add sample.txt",
            "git -c user.name=Synthetic commit -m test",
            "git --git-dir=.git reset HEAD",
            f"{git_path} commit -m test",
            "git status && git add sample.txt",
            "printf ok\ngit switch other",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assertTrue(agent.tool_bash({"command": command}).startswith("BLOCKED:"))

    def test_bash_preserves_git_inspection_commands(self):
        commands = [
            "git status --short",
            "git diff --check",
            "git rev-parse --show-toplevel",
            "git branch --show-current",
            "git config --get user.name",
        ]
        for command in commands:
            with self.subTest(command=command):
                result = agent.tool_bash({"command": command})
                self.assertTrue(result.startswith("exit_code="), result)

    def test_bash_blocks_mutating_branch_remote_and_config_forms(self):
        commands = [
            "git branch new-branch",
            "git branch -D old-branch",
            "git remote add origin https://example.invalid/repo.git",
            "git remote remove origin",
            "git config user.name Synthetic",
            "git config --unset user.name",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assertTrue(agent.tool_bash({"command": command}).startswith("BLOCKED:"))

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

    def test_tool_signature_is_canonical_and_includes_tool_name(self):
        first = agent.canonical_tool_signature(
            "read", {"path": "sample.py", "max_lines": 20}
        )
        reordered = agent.canonical_tool_signature(
            "read", {"max_lines": 20, "path": "sample.py"}
        )
        other_tool = agent.canonical_tool_signature(
            "inspect", {"max_lines": 20, "path": "sample.py"}
        )
        self.assertEqual(first, reordered)
        self.assertNotEqual(first, other_tool)

    def test_pre_write_guard_allows_distinct_calls_and_resets_after_write(self):
        guard = agent.PreWriteExplorationGuard(enabled=True, budget=3)
        self.assertIsNone(guard.check("read", {"path": "one.py"}))
        self.assertIsNone(guard.check("read", {"path": "two.py"}))
        guard.note_successful_write()
        self.assertIsNone(guard.check("bash", {"command": "pytest -q"}))
        self.assertFalse(guard.exhausted)

    def test_pre_write_guard_blocks_repeated_read_only_call(self):
        guard = agent.PreWriteExplorationGuard(enabled=True)
        args = {"query": "needle", "path": "."}
        self.assertIsNone(guard.check("search", args))
        result = guard.check("search", {"path": ".", "query": "needle"})
        self.assertTrue(result.startswith("BLOCKED:"))
        self.assertEqual(guard.reason, "exploration_budget_exhausted")
        self.assertEqual(guard.trigger, "repeated_read_only_call")
        self.assertEqual(
            guard.signature_hash,
            agent.tool_signature_hash("search", args),
        )
        self.assertNotIn("needle", guard.signature_hash)

    def test_metrics_prints_agent_limit_details(self):
        agent.METRICS_DIR = self.root / "metrics"
        agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
        agent.METRICS_PRUNED = False
        agent.record_metric_event({"type": "run_start"})
        agent.record_metric_event({
            "type": "agent_limit",
            "reason": "exploration_budget_exhausted",
            "trigger": "budget_reached",
            "exploration_calls": 6,
            "exploration_budget": 6,
        })
        agent.record_metric_event({
            "type": "agent_limit",
            "reason": "overall_round_limit_reached",
            "round_limit": 12,
        })
        output = io.StringIO()
        with redirect_stdout(output):
            agent.print_lai_metrics()
        shown = output.getvalue()
        self.assertIn("exploration_budget_exhausted", shown)
        self.assertIn("trigger=budget_reached", shown)
        self.assertIn("exploration=6/6", shown)
        self.assertIn("overall_round_limit_reached round_limit=12", shown)

    def test_audit_prints_agent_limit_details_without_signature(self):
        agent.AUDIT_DIR = self.root / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
        agent.record_audit_event({
            "type": "agent_limit",
            "reason": "exploration_budget_exhausted",
            "trigger": "repeated_read_only_call",
            "exploration_calls": 1,
            "exploration_budget": 6,
            "signature_hash": "a" * 64,
        })
        agent.record_audit_event({
            "type": "agent_limit",
            "reason": "overall_round_limit_reached",
            "round_limit": 14,
        })
        output = io.StringIO()
        with redirect_stdout(output):
            agent.print_lai_audit()
        shown = output.getvalue()
        self.assertIn("Reason: exploration_budget_exhausted", shown)
        self.assertIn("Trigger: repeated_read_only_call", shown)
        self.assertIn("Exploration: 1/6", shown)
        self.assertIn("Reason: overall_round_limit_reached", shown)
        self.assertIn("Round limit: 14", shown)
        self.assertNotIn("a" * 64, shown)

    def test_patch_dispatch_records_hashes_and_tool_metric(self):
        target = self.root / "sample.txt"
        target.write_text("before")
        agent.METRICS_DIR = self.root / "metrics"
        agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
        agent.AUDIT_DIR = self.root / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
        agent.METRICS_PRUNED = False
        result = agent.run_tool("patch", {"changes": [
            {"path": "sample.txt", "old": "before", "new": "after"},
        ]})
        self.assertTrue(result.startswith("OK:"))
        audit = json.loads(agent.AUDIT_FILE.read_text())
        self.assertNotEqual(audit["before_hashes"], audit["after_hashes"])
        metric = json.loads(agent.METRICS_FILE.read_text())
        self.assertEqual(metric["name"], "patch")
        self.assertTrue(metric["ok"])

    def test_workspace_state_round_trip_and_handoff(self):
        state = agent.load_workspace_state()
        state["last_mode"] = "test"
        state["last_task"] = "synthetic task"
        state["recent_files"] = ["sample.txt"]
        handoff_path = agent.save_workspace_state(state)
        loaded = agent.load_workspace_state()
        self.assertEqual(loaded["last_task"], "synthetic task")
        self.assertIn("sample.txt", handoff_path.read_text())
        current = agent.STATE_BASE.parent / "current-context.md"
        self.assertIn("synthetic task", current.read_text())
        agent.clear_workspace_state()
        self.assertFalse(handoff_path.exists())
        self.assertFalse(current.exists())

    def test_api_key_file_is_configurable(self):
        key_file = self.root / "key"
        key_file.write_text("synthetic-test-key\n")
        agent.CONFIG["api_key_file"] = key_file
        self.assertEqual(agent.llama_api_key(), "synthetic-test-key")

    def test_configuration_precedence_cli_over_env_over_toml_over_defaults(self):
        config_dir = self.root / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.toml"
        config_file.write_text(
            "[lai]\n"
            "host = 'toml-host'\n"
            "port = 7001\n"
            "model = 'toml-model'\n"
        )
        values, remaining = agent.load_configuration(
            ["--config", str(config_file), "--host", "cli-host", "--fix", "task"],
            environ={"LAI_HOST": "env-host", "LAI_PORT": "7002"},
            home=self.root,
        )
        self.assertEqual(values["host"], "cli-host")
        self.assertEqual(values["port"], 7002)
        self.assertEqual(values["model"], "toml-model")
        self.assertEqual(remaining, ["--fix", "task"])

    def test_configuration_uses_xdg_defaults_and_rejects_invalid_port(self):
        values, _ = agent.load_configuration([], environ={}, home=self.root)
        self.assertEqual(values["config_dir"], self.root / ".config" / "lai")
        self.assertEqual(values["data_dir"], self.root / ".local" / "share" / "lai")
        with self.assertRaisesRegex(SystemExit, "port"):
            agent.load_configuration(["--port", "invalid"], environ={}, home=self.root)

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

    def test_deterministic_version_command_needs_no_server(self):
        result = subprocess.run(
            [str(SOURCE), "--version"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "lai-local-agent 0.4.0-alpha.1")

    def test_deterministic_show_config_obeys_cli_without_server(self):
        result = subprocess.run(
            [str(SOURCE), "--host", "127.0.0.9", "--port", "9012", "--show-config"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        shown = json.loads(result.stdout)
        self.assertEqual(shown["host"], "127.0.0.9")
        self.assertEqual(shown["port"], 9012)


if __name__ == "__main__":
    unittest.main()
