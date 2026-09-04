import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
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


def make_spec_text(mode="full", status="active", requirement="REQ-001"):
    text = (
        "# Spec: Synthetic\n\n"
        "## Metadata\n\n"
        f"- Mode: `{mode}`\n"
        f"- Status: `{status}`\n\n"
        "## Goal\n\nSynthetic goal.\n\n"
        "## Requirements\n\n"
        f"### {requirement}\n\nSynthetic requirement.\n\n"
        "## Acceptance Criteria\n\n- Observable result.\n\n"
        "## Validation\n\n"
        f"- `{requirement}`: synthetic check.\n"
    )
    if mode == "full":
        text += (
            "\n## Context and Constraints\n\nSynthetic context.\n"
            "\n## Non-Goals\n\n- Synthetic non-goal.\n"
            "\n## Implementation Notes\n\nSynthetic notes.\n"
            "\n## Traceability\n\n"
            f"- `{requirement}` -> synthetic check\n"
        )
    return text


class LocalAgentTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        agent.ROOT = self.root.resolve()
        agent.STATE_BASE = self.root / ".lai-data" / "state"
        agent.CONFIG["api_key_file"] = self.root / "key"
        agent.read_paths.clear()
        agent.full_read_hashes.clear()

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

    def test_search_falls_back_when_rg_is_unavailable(self):
        (self.root / "fallback.txt").write_text(
            "alpha\nneedle fallback\nomega\n"
        )

        original_run = agent.subprocess.run

        def missing_rg(*args, **kwargs):
            raise FileNotFoundError("rg")

        agent.subprocess.run = missing_rg
        try:
            result = agent.tool_search({
                "path": ".",
                "query": "needle",
            })
        finally:
            agent.subprocess.run = original_run

        self.assertIn(
            "fallback.txt:2:needle fallback",
            result,
        )

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

    def test_rewrite_requires_full_inspection(self):
        target = self.root / "sample.txt"
        target.write_text("one\ntwo\nthree\n")

        agent.tool_read({
            "path": "sample.txt",
            "start_line": 1,
            "max_lines": 1,
        })

        result = agent.tool_rewrite({
            "path": "sample.txt",
            "content": "replaced\n",
        })

        self.assertIn(
            "requires a full inspection",
            result,
        )
        self.assertEqual(
            target.read_text(),
            "one\ntwo\nthree\n",
        )

    def test_implement_read_fully_exposes_small_file_for_rewrite(self):
        target = self.root / "sample.txt"
        target.write_text(
            "".join(
                f"line-{index}\n"
                for index in range(1, 62)
            )
        )

        old_mode = agent.ACTIVE_MODE
        agent.ACTIVE_MODE = "implement"

        try:
            read_result = agent.tool_read({
                "path": "sample.txt",
                "start_line": 1,
                "max_lines": 60,
            })
        finally:
            agent.ACTIVE_MODE = old_mode

        self.assertIn(
            "lines 1-61 of 61",
            read_result,
        )
        self.assertIn(
            "sample.txt",
            agent.full_read_hashes,
        )

        target.chmod(0o755)

        result = agent.tool_rewrite({
            "path": "sample.txt",
            "content": "replacement = True\n",
        })

        self.assertTrue(
            result.startswith("OK: rewritten")
        )
        self.assertEqual(
            target.read_text(),
            "replacement = True\n",
        )
        self.assertTrue(
            target.stat().st_mode & 0o100
        )

    def test_rewrite_refuses_file_changed_after_inspection(self):
        target = self.root / "sample.txt"
        target.write_text("before\n")

        agent.tool_read({
            "path": "sample.txt",
            "start_line": 1,
            "max_lines": 80,
        })

        target.write_text("external change\n")

        result = agent.tool_rewrite({
            "path": "sample.txt",
            "content": "replacement\n",
        })

        self.assertIn(
            "changed after inspection",
            result,
        )
        self.assertEqual(
            target.read_text(),
            "external change\n",
        )

    def test_rewrite_refuses_symlink_even_inside_repository(self):
        target = self.root / "target.txt"
        target.write_text("before\n")
        link = self.root / "link.txt"
        link.symlink_to(target)

        result = agent.tool_rewrite({
            "path": "link.txt",
            "content": "replacement\n",
        })

        self.assertIn(
            "refuses symlink",
            result,
        )
        self.assertEqual(
            target.read_text(),
            "before\n",
        )

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
        (self.root / "sample.txt").write_text("sample\n")
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

    def test_workspace_state_prunes_unverified_paths_on_save(self):
        sample = self.root / "sample.txt"
        sample.write_text("sample\n")

        directory = self.root / "nested"
        directory.mkdir()

        outside = (
            self.root.parent
            / f"{self.root.name}-outside.txt"
        )
        outside.write_text("outside\n")

        try:
            state = agent.load_workspace_state()
            state["recent_files"] = [
                "sample.txt",
                "missing.py",
                str(sample),
                str(directory),
                str(self.root),
                str(outside),
                "../outside.txt",
            ]
            state["modified_files"] = [
                str(sample),
                "missing.py",
                str(outside),
            ]

            handoff_path = agent.save_workspace_state(state)
            loaded = agent.load_workspace_state()

            self.assertEqual(
                loaded["recent_files"],
                ["sample.txt"],
            )
            self.assertEqual(
                loaded["modified_files"],
                ["sample.txt"],
            )

            handoff = handoff_path.read_text()

            self.assertIn("- sample.txt", handoff)
            self.assertNotIn("missing.py", handoff)
            self.assertNotIn(str(outside), handoff)
            self.assertNotIn(f"- {self.root}", handoff)
            self.assertNotIn(f"- {sample}", handoff)

        finally:
            outside.unlink(missing_ok=True)

    def test_workspace_state_prunes_legacy_invalid_paths_on_load(self):
        sample = self.root / "sample.txt"
        sample.write_text("sample\n")

        json_path, _ = agent.workspace_state_paths()
        json_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        json_path.write_text(
            json.dumps({
                "root": str(agent.ROOT),
                "recent_files": [
                    "sample.txt",
                    "ghost.py",
                    str(self.root),
                ],
                "modified_files": [
                    "ghost.py",
                    str(sample),
                ],
            })
        )

        loaded = agent.load_workspace_state()

        self.assertEqual(
            loaded["recent_files"],
            ["sample.txt"],
        )
        self.assertEqual(
            loaded["modified_files"],
            ["sample.txt"],
        )

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

    def test_load_mode_skill_prefers_standard_skill(self):
        skills = self.root / "skills"
        standard = skills / "fix" / "SKILL.md"
        standard.parent.mkdir(parents=True)
        standard.write_text(
            "---\nname: fix\ndescription: Use when fixing a bug safely.\n"
            "---\n\nSTANDARD\n"
        )
        (skills / "fix.txt").write_text("LEGACY\n")

        self.assertEqual(agent.load_mode_skill("fix", skills), "STANDARD")

    def test_load_mode_skill_falls_back_to_legacy(self):
        skills = self.root / "skills"
        skills.mkdir()
        (skills / "plan.txt").write_text("LEGACY PLAN\n")

        self.assertEqual(
            agent.load_mode_skill("plan", skills),
            "LEGACY PLAN",
        )

    def test_invalid_standard_skill_does_not_fall_back(self):
        skills = self.root / "skills"
        standard = skills / "fix" / "SKILL.md"
        standard.parent.mkdir(parents=True)
        standard.write_text("---\nname: wrong\ndescription: Invalid.\n---\n\nBODY\n")
        (skills / "fix.txt").write_text("LEGACY\n")

        with self.assertRaisesRegex(SystemExit, "Invalid skill"):
            agent.load_mode_skill("fix", skills)

    def test_main_loads_standard_skill_into_system_prompt(self):
        skills = self.root / "skills"
        skill = skills / "fix" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(
            "---\nname: fix\n"
            "description: Use when fixing a synthetic bug safely.\n"
            "---\n\nSTANDARD FIX BODY\n"
        )

        captured = {}

        def stop_at_model(host, messages, **kwargs):
            captured["messages"] = messages
            raise RuntimeError("STOP_AT_MODEL")

        with mock.patch.object(agent, "CLI_ARGS", ["--fix", "synthetic task"]), \
             mock.patch.object(agent, "SKILLS_DIR", skills), \
             mock.patch.object(agent, "server_ready", return_value=True), \
             mock.patch.object(agent, "api_call", side_effect=stop_at_model), \
             mock.patch.object(agent, "record_metric_event"), \
             mock.patch.object(agent, "record_audit_event"):
            with self.assertRaisesRegex(RuntimeError, "STOP_AT_MODEL"):
                agent.main()

        system = captured["messages"][0]["content"]
        self.assertIn("ACTIVE SKILL:\nSTANDARD FIX BODY", system)

    def test_load_mode_skill_reports_missing_skill(self):
        skills = self.root / "skills"
        skills.mkdir()

        with self.assertRaisesRegex(SystemExit, "Skill não encontrada"):
            agent.load_mode_skill("debug", skills)

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

    def test_post_patch_sanity_catches_python_syntax_error(self):
        target = self.root / "sample.py"
        target.write_text("VALUE = 1\n")

        subprocess.run(
            ["git", "add", "sample.py"],
            cwd=self.root,
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
            cwd=self.root,
            check=True,
        )

        target.write_text("def broken(:\n    pass\n")

        result = agent.post_patch_sanity(
            "unused",
            "fix syntax",
            ["sample.py"],
        )

        self.assertIsNotNone(result)
        self.assertIn("Python syntax check failed", result)
        self.assertIn("sample.py", result)

    def test_parse_spec_accepts_valid_full_spec(self):
        path = self.root / "001-feature.md"
        path.write_text(make_spec_text())

        spec = agent.parse_spec(path)

        self.assertEqual(spec["mode"], "full")
        self.assertEqual(spec["status"], "active")
        self.assertEqual(spec["requirements"], ["REQ-001"])

    def test_parse_spec_rejects_invalid_workflow_mode(self):
        path = self.root / "001-feature.md"
        path.write_text(make_spec_text(mode="fast"))

        with self.assertRaisesRegex(ValueError, "quick or full"):
            agent.parse_spec(path)

    def test_parse_spec_requires_full_only_sections(self):
        path = self.root / "001-feature.md"
        text = make_spec_text().replace(
            "\n## Non-Goals\n\n- Synthetic non-goal.\n",
            "",
        )
        path.write_text(text)

        with self.assertRaisesRegex(ValueError, "full spec missing"):
            agent.parse_spec(path)

    def test_parse_spec_rejects_invalid_requirement_id(self):
        path = self.root / "001-feature.md"
        path.write_text(make_spec_text(requirement="REQ-1"))

        with self.assertRaisesRegex(ValueError, "REQ-NNN"):
            agent.parse_spec(path)

    def test_parse_spec_requires_full_traceability_coverage(self):
        path = self.root / "001-feature.md"
        text = make_spec_text().replace(
            "- `REQ-001` -> synthetic check",
            "- synthetic mapping",
        )
        path.write_text(text)

        with self.assertRaisesRegex(ValueError, "traceability missing: REQ-001"):
            agent.parse_spec(path)

    def test_parse_spec_requires_validation_traceability(self):
        path = self.root / "001-feature.md"
        text = make_spec_text().replace(
            "- `REQ-001`: synthetic check.",
            "- synthetic check.",
        )
        path.write_text(text)

        with self.assertRaisesRegex(ValueError, "validation missing: REQ-001"):
            agent.parse_spec(path)

    def test_load_active_spec_ignores_drafts(self):
        specs = self.root / ".specs"
        specs.mkdir()
        (specs / "001-draft.md").write_text(
            make_spec_text(status="draft")
        )

        self.assertIsNone(agent.load_active_spec(self.root))

    def test_load_active_spec_rejects_symlinked_spec_file(self):
        specs = self.root / ".specs"
        specs.mkdir()
        outside = self.root / "outside-spec.md"
        outside.write_text(make_spec_text())
        (specs / "001-link.md").symlink_to(outside)

        with self.assertRaisesRegex(SystemExit, "must not be a symlink"):
            agent.load_active_spec(self.root)

    def test_load_active_spec_rejects_multiple_active_specs(self):
        specs = self.root / ".specs"
        specs.mkdir()
        (specs / "001-first.md").write_text(make_spec_text())
        (specs / "002-second.md").write_text(make_spec_text())

        with self.assertRaisesRegex(SystemExit, "Multiple active specs"):
            agent.load_active_spec(self.root)

    def test_render_active_spec_context_uses_workflow_mode(self):
        path = self.root / "001-feature.md"
        path.write_text(make_spec_text(mode="quick"))

        rendered = agent.render_active_spec_context(agent.parse_spec(path))

        self.assertIn("Workflow: quick", rendered)
        self.assertIn("narrow exploration", rendered)
        self.assertIn("cannot override AGENTS.md", rendered)
        self.assertIn("REQ-001", rendered)

    def test_main_injects_active_spec_into_system_prompt(self):
        specs = self.root / ".specs"
        specs.mkdir()
        (specs / "001-feature.md").write_text(make_spec_text())
        captured = {}

        def stop_at_model(host, messages, **kwargs):
            captured["messages"] = messages
            raise RuntimeError("STOP_AT_MODEL")

        with mock.patch.object(agent, "CLI_ARGS", ["synthetic task"]), \
             mock.patch.object(agent, "server_ready", return_value=True), \
             mock.patch.object(agent, "api_call", side_effect=stop_at_model), \
             mock.patch.object(agent, "record_metric_event"), \
             mock.patch.object(agent, "record_audit_event"):
            with self.assertRaisesRegex(RuntimeError, "STOP_AT_MODEL"):
                agent.main()

        system = captured["messages"][0]["content"]
        self.assertIn("ACTIVE SPEC (normative for this change)", system)
        self.assertIn("Workflow: full", system)
        self.assertIn("REQ-001", system)

    def test_deterministic_spec_status_needs_no_server(self):
        specs = self.root / ".specs"
        specs.mkdir()
        (specs / "001-feature.md").write_text(make_spec_text())

        result = subprocess.run(
            [str(SOURCE), "--spec-status"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("# LAI Active Spec", result.stdout)
        self.assertIn("Path: .specs/001-feature.md", result.stdout)
        self.assertIn("Mode: full", result.stdout)
        self.assertIn("Requirements: REQ-001", result.stdout)

    def test_deterministic_version_command_needs_no_server(self):
        result = subprocess.run(
            [str(SOURCE), "--version"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "lai-local-agent 0.4.0-alpha.7")

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
