import importlib.util
from importlib.machinery import SourceFileLoader
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stdout


SOURCE = Path(__file__).parents[1] / "src" / "local-agent"
if str(SOURCE.parent) not in sys.path:
    sys.path.insert(0, str(SOURCE.parent))
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
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        agent.ROOT = self.root.resolve()
        agent.STATE_BASE = self.base / "data" / "state"
        agent.RUN_CHECKPOINT_CONTEXT = None
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

    def test_policy_classifies_sensitive_shell_commands(self):
        cases = {
            "git commit -m test": "ASK",
            "pip install package": "ASK",
            "npm add package": "ASK",
            "sudo true": "DENY",
            "rm -rf generated": "DENY",
            "git push --force origin main": "DENY",
            "git reset --hard HEAD~1": "DENY",
            "npm publish": "DENY",
            "Remove-Item C:\\temp -Recurse -Force": "DENY",
            "docker compose down": "DENY",
            "TRUNCATE TABLE records": "DENY",
            "git status --short": "ALLOW",
            "python3 -m pytest -q": "ALLOW",
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                policy = agent.evaluate_tool_policy("bash", {"command": command})
                self.assertEqual(policy["decision"], expected)


    def test_command_help_is_successful_and_non_executing(self):
        cases = {
            "--control-token": "Usage: lai control-token",
            "--control-serve": "Usage: lai serve",
            "--sessions": "Usage: lai sessions",
            "--run": "Usage: lai runs",
            "--runs": "Usage: lai runs",
            "--model-eval": "Usage: lai model",
            "--update-intelligence": "Usage: lai update",
            "--release-check": "Usage: lai release-check",
            "--release-pack": "Usage: lai release-pack",
            "--release-governance": "Usage: lai release-governance",
            "--project-handoff": "Usage: lai project-handoff",
            "--workspace": "Usage: lai workspace",
            "--readiness": "Usage: lai readiness",
            "--gateway-contract": "Usage: lai gateway-contract",
            "--policy-check": "Usage: lai policy-check",
            "--recovery": "Usage: lai recovery",
            "--semantics": "Usage: lai semantics",
            "--status": "Usage: lai status",
            "--metrics": "Usage: lai metrics",
            "--audit": "Usage: lai audit",
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                buffer = io.StringIO()
                with mock.patch.object(agent, "CLI_ARGS", [command, "--help"]), \
                        mock.patch.object(agent, "api_call") as api_call, \
                        mock.patch.object(agent, "record_metric_event") as metric, \
                        redirect_stdout(buffer):
                    agent.main()
                self.assertIn(expected, buffer.getvalue())
                api_call.assert_not_called()
                metric.assert_not_called()

    def test_mode_help_is_successful_and_non_executing(self):
        for command in [
            "--plan",
            "--debug",
            "--diagnose",
            "--review",
            "--security",
            "--release",
            "--fix",
            "--ci-fix",
            "--test",
            "--refactor",
            "--implement",
        ]:
            with self.subTest(command=command):
                buffer = io.StringIO()
                with mock.patch.object(agent, "CLI_ARGS", [command, "--help"]), \
                        mock.patch.object(agent, "api_call") as api_call, \
                        mock.patch.object(agent, "record_metric_event") as metric, \
                        redirect_stdout(buffer):
                    agent.main()
                self.assertIn("Usage: lai <mode> <task>", buffer.getvalue())
                self.assertIn("Mode help is deterministic", buffer.getvalue())
                api_call.assert_not_called()
                metric.assert_not_called()

    def test_web_cli_search_fetch_help_and_errors_are_deterministic(self):
        search_payload = {
            "query": "safe harness",
            "provider": "duckduckgo-lite",
            "provider_url": "https://lite.duckduckgo.com/lite/?q=safe+harness",
            "resolved_ips": ["93.184.216.34"],
            "connected_ip": "93.184.216.34",
            "status": 200,
            "fetched_at": "2026-09-06T02:00:00Z",
            "result_count": 1,
            "results": [{"title": "Example", "url": "https://example.com/", "snippet": "sample"}],
            "response_sha256": "a" * 64,
            "untrusted_external_content": True,
        }
        fetch_payload = {
            "requested_url": "https://example.com/",
            "url": "https://example.com/",
            "host": "example.com",
            "resolved_ips": ["93.184.216.34"],
            "connected_ip": "93.184.216.34",
            "status": 200,
            "content_type": "text/plain",
            "fetched_at": "2026-09-06T02:00:00Z",
            "sha256": "b" * 64,
            "body_bytes": 6,
            "text": "sample",
            "truncated": False,
            "untrusted_external_content": True,
        }
        with mock.patch.object(agent, "search_web_evidence", return_value=search_payload) as searched, \
                mock.patch.object(agent, "fetch_web_evidence", return_value=fetch_payload) as fetched:
            output = io.StringIO()
            with redirect_stdout(output):
                agent.handle_web_evidence(["search", "safe", "harness", "--max-results", "3", "--json"])
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["result_count"], 1)
            searched.assert_called_once_with("safe harness", max_results=3)

            output = io.StringIO()
            with redirect_stdout(output):
                agent.handle_web_evidence(["fetch", "https://example.com/", "--max-chars", "200", "--json"])
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["url"], "https://example.com/")
            fetched.assert_called_once_with("https://example.com/", max_chars=200)

        output = io.StringIO()
        with redirect_stdout(output):
            agent.handle_web_evidence(["--help"])
        self.assertIn("Usage: lai web search", output.getvalue())

        with self.assertRaisesRegex(SystemExit, "max-chars must be between 200"):
            agent.handle_web_evidence(["fetch", "https://example.com/", "--max-chars", "199"])

        with mock.patch.object(agent, "fetch_web_evidence", side_effect=ValueError("only HTTPS URLs are allowed")):
            with self.assertRaisesRegex(SystemExit, "only HTTPS URLs are allowed"):
                agent.handle_web_evidence(["fetch", "http://example.com/"])

    def test_web_tools_are_read_only_policy_and_return_untrusted_evidence(self):
        search_payload = {
            "query": "example",
            "provider": "duckduckgo-lite",
            "provider_url": "https://lite.duckduckgo.com/lite/?q=example",
            "resolved_ips": ["93.184.216.34"],
            "connected_ip": "93.184.216.34",
            "status": 200,
            "fetched_at": "2026-09-06T02:00:00Z",
            "result_count": 1,
            "results": [{"title": "Example", "url": "https://example.com/", "snippet": "sample"}],
            "response_sha256": "a" * 64,
            "untrusted_external_content": True,
        }
        fetch_payload = {
            "requested_url": "https://example.com/",
            "url": "https://example.com/",
            "host": "example.com",
            "resolved_ips": ["93.184.216.34"],
            "connected_ip": "93.184.216.34",
            "status": 200,
            "content_type": "text/plain",
            "fetched_at": "2026-09-06T02:00:00Z",
            "sha256": "b" * 64,
            "body_bytes": 6,
            "text": "sample",
            "truncated": False,
            "untrusted_external_content": True,
        }
        audits = []
        with mock.patch.object(agent, "search_web_evidence", return_value=search_payload), \
                mock.patch.object(agent, "fetch_web_evidence", return_value=fetch_payload), \
                mock.patch.object(agent, "record_audit_event", side_effect=audits.append):
            searched = agent.tool_web_search({"query": "example"})
            fetched = agent.tool_web_fetch({"url": "https://example.com/"})
        self.assertIn("EXTERNAL WEB EVIDENCE (UNTRUSTED)", searched)
        self.assertIn("EXTERNAL WEB EVIDENCE (UNTRUSTED)", fetched)
        self.assertEqual(agent.evaluate_tool_policy("web_search", {"query": "x"}, mode="review")["decision"], "ALLOW")
        self.assertEqual(agent.evaluate_tool_policy("web_fetch", {"url": "https://example.com"}, mode="security")["decision"], "ALLOW")
        self.assertNotIn("sample", json.dumps(audits))
        self.assertNotIn("https://example.com/", json.dumps(audits))
        self.assertIn("query_sha256", audits[0])
        self.assertIn("url_sha256", audits[1])

    def test_policy_check_renders_deterministic_non_execution_evidence(self):
        payload = json.loads(
            agent.render_policy_check(
                [
                    "--tool",
                    "bash",
                    "--command",
                    "git status --short",
                    "--mode",
                    "unknown",
                    "--json",
                ]
            )
        )
        self.assertEqual(payload["decision"], "ALLOW")
        self.assertFalse(payload["executed"])
        self.assertEqual(payload["tool"], "bash")

        denied = json.loads(
            agent.render_policy_check(
                ["--stdin", "--json"],
                stdin_text=json.dumps(
                    {
                        "tool": "bash",
                        "args": {"command": "npm publish"},
                        "mode": "unknown",
                    }
                ),
            )
        )
        self.assertEqual(denied["decision"], "DENY")
        self.assertFalse(denied["executed"])

    def test_policy_check_rejects_malformed_or_conflicting_input(self):
        with self.assertRaises(SystemExit):
            agent.render_policy_check(["--stdin", "--json"], stdin_text="{bad")
        with self.assertRaises(SystemExit):
            agent.render_policy_check(["--stdin", "--tool", "bash", "--json"], stdin_text="{}")


    def test_direct_local_agent_release_check_subcommand_is_deterministic(self):
        result = subprocess.run(
            [str(SOURCE), "release-check", "--target", agent.VERSION, "--json"],
            cwd=self.root,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertIn(result.returncode, {0, 1})
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], agent.VERSION)
        self.assertIn(payload["overall"], {"ready", "blocked"})

    def test_operating_mode_command_is_deterministic_and_policy_aligned(self):
        result = subprocess.run(
            [str(SOURCE), "operating-mode", "--json"],
            cwd=self.root,
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "local_first_milestone_batches")
        self.assertEqual(payload["external_evidence"]["mode"], "read_only_untrusted_evidence")
        self.assertIn("product progress", payload["decision_gate"]["before_action"])
        self.assertIn("bounded directly related deliverable", payload["decision_gate"]["before_exit_or_sync"])
        self.assertIn("scope creep", payload["decision_gate"]["stop_when"])
        self.assertIn("focused tests", payload["development"]["feedback"])
        self.assertIn("required capabilities", payload["compatibility"]["preference"])

        text_result = subprocess.run(
            [str(SOURCE), "operating-mode"],
            cwd=self.root,
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )
        self.assertIn("# lai operating mode", text_result.stdout)
        self.assertIn("Decision gate", text_result.stdout)
        self.assertIn("External evidence", text_result.stdout)
        self.assertNotIn("sk-", text_result.stdout)

    def test_top_level_help_is_successful_and_non_executing(self):
        for args in (["--help"], ["-h"], ["help"]):
            proc = subprocess.run(
                [str(SOURCE), *args],
                cwd=self.root,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("Usage: lai <command> [options]", proc.stdout)
            for command in (
                "status",
                "readiness | ready",
                "recovery",
                "checkpoint",
                "snapshot",
                "rollback",
                "mcp",
                "web",
                "metrics | audit",
                "spec | semantic",
                "release-check",
                "workspace",
                "operating-mode",
                "context",
            ):
                self.assertIn(command, proc.stdout)
            self.assertEqual(proc.stderr, "")

    def test_mcp_help_is_successful_and_non_executing(self):
        cases = [
            (["--help"], "Usage: lai mcp [status|tools|policy-check]"),
            (["help"], "Usage: lai mcp [status|tools|policy-check]"),
            (["status", "--help"], "Usage: lai mcp status [--json]"),
            (["tools", "--help"], "Usage: lai mcp tools [--json]"),
            (["policy-check", "--help"], "Usage: lai mcp policy-check"),
        ]
        for args, expected in cases:
            with self.subTest(args=args):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    agent.handle_mcp(args)
                output = buffer.getvalue()
                self.assertIn(expected, output)
                self.assertNotIn("# lai mcp status", output)
                self.assertNotIn("# lai mcp tools", output)

    def test_mcp_status_and_tools_reject_unknown_flags(self):
        with self.assertRaises(SystemExit):
            agent.handle_mcp(["status", "--bogus"])
        with self.assertRaises(SystemExit):
            agent.handle_mcp(["tools", "--bogus"])
        with self.assertRaises(SystemExit):
            agent.handle_mcp(["status", "--help", "--bogus"])
        with self.assertRaises(SystemExit):
            agent.handle_mcp(["tools", "--help", "--bogus"])

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            agent.handle_mcp(["policy-check", "--help"])
        policy_output = buffer.getvalue()
        self.assertIn("Usage: lai mcp policy-check", policy_output)
        self.assertNotIn("DENY", policy_output)

        with self.assertRaises(SystemExit):
            agent.handle_mcp(["policy-check"])

    def test_mcp_status_discovers_config_and_never_prints_secret_values(self):
        empty_payload = json.loads(agent.render_mcp_status(json_mode=True))
        self.assertEqual(empty_payload["overall"], "no_config")
        self.assertFalse(empty_payload["security"]["executes_tools"])
        self.assertFalse(empty_payload["security"]["reads_env_values"])

        mcp_dir = self.root / ".cursor"
        mcp_dir.mkdir()
        (mcp_dir / "mcp.json").write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "desktop-commander": {
                            "command": "npx",
                            "args": ["--yes", "@wonderwhy-er/desktop-commander@latest", "remote"],
                            "env": {"DESKTOP_COMMANDER_TOKEN": "${DESKTOP_COMMANDER_TOKEN}"},
                        }
                    }
                }
            )
        )
        valid_payload = json.loads(agent.render_mcp_status(json_mode=True))
        self.assertEqual(valid_payload["overall"], "ready")
        self.assertEqual(valid_payload["servers"][0]["name"], "desktop-commander")
        self.assertEqual(valid_payload["servers"][0]["unsafe_env_keys"], [])
        self.assertIn("DESKTOP_COMMANDER_TOKEN", valid_payload["servers"][0]["env_keys"])
        self.assertNotIn("${DESKTOP_COMMANDER_TOKEN}", json.dumps(valid_payload))

        (self.root / ".mcp.json").write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "bad": {
                            "command": "node",
                            "env": {"API_TOKEN": "literal-secret-value-that-must-not-appear"},
                        }
                    }
                }
            )
        )
        blocked_payload = json.loads(agent.render_mcp_status(json_mode=True))
        self.assertEqual(blocked_payload["overall"], "blocked")
        self.assertIn("API_TOKEN", json.dumps(blocked_payload))
        self.assertNotIn("literal-secret-value-that-must-not-appear", json.dumps(blocked_payload))

    def test_mcp_tools_and_policy_check_are_non_executing_foundation(self):
        (self.root / ".mcp.json").write_text(
            json.dumps({"mcpServers": {"local": {"command": "node", "args": ["server.js"]}}})
        )
        tools = json.loads(agent.render_mcp_tools(json_mode=True))
        self.assertFalse(tools["execution_enabled"])
        self.assertEqual(tools["servers"][0]["name"], "local")

        status_policy = json.loads(agent.render_mcp_policy_check(["--operation", "status", "--json"]))
        self.assertEqual(status_policy["decision"], "ALLOW")
        self.assertFalse(status_policy["executed"])

        list_policy = json.loads(
            agent.render_mcp_policy_check(
                ["--operation", "list-tools", "--server", "local", "--json"]
            )
        )
        self.assertEqual(list_policy["decision"], "ALLOW")
        self.assertFalse(list_policy["executed"])

        call_policy = json.loads(
            agent.render_mcp_policy_check(
                [
                    "--operation",
                    "call-tool",
                    "--server",
                    "local",
                    "--tool",
                    "read_file",
                    "--json",
                ]
            )
        )
        self.assertEqual(call_policy["decision"], "DENY")
        self.assertFalse(call_policy["executed"])

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
                self.assertTrue(result.startswith("POLICY ASK:"), result)
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
                self.assertTrue(agent.tool_bash({"command": command}).startswith("POLICY ASK:"))

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
                self.assertTrue(agent.tool_bash({"command": command}).startswith("POLICY ASK:"))

    def test_policy_ask_and_deny_do_not_execute(self):
        commands = [
            ("git commit -m test", "POLICY ASK:"),
            ("pip install package", "POLICY ASK:"),
            ("rm -rf generated", "POLICY DENY:"),
            ("sudo true", "POLICY DENY:"),
        ]
        for command, prefix in commands:
            with self.subTest(command=command):
                with mock.patch.object(agent.subprocess, "run") as run:
                    result = agent.tool_bash({"command": command})
                self.assertTrue(result.startswith(prefix), result)
                run.assert_not_called()

    def test_policy_blocks_write_tools_in_read_only_modes(self):
        old_mode = agent.ACTIVE_MODE
        try:
            agent.ACTIVE_MODE = "review"
            policy = agent.evaluate_tool_policy("patch", {"changes": []})
        finally:
            agent.ACTIVE_MODE = old_mode
        self.assertEqual(policy["decision"], "DENY")
        self.assertIn("review", policy["reason"])

    def test_policy_decision_is_audited_by_dispatcher(self):
        agent.AUDIT_DIR = self.root / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
        agent.METRICS_DIR = self.root / "metrics"
        agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
        with mock.patch.object(agent.subprocess, "run") as run:
            result = agent.run_tool("bash", {"command": "git commit -m test"})
        self.assertTrue(result.startswith("POLICY ASK:"), result)
        run.assert_not_called()
        event = json.loads(agent.AUDIT_FILE.read_text())
        self.assertEqual(event["type"], "policy_decision")
        self.assertEqual(event["tool"], "bash")
        self.assertEqual(event["decision"], "ASK")
        self.assertIn("git commit", event["reason"])

    def test_metrics_and_audit_write_jsonl(self):
        agent.METRICS_DIR = self.root / "metrics"
        agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
        agent.AUDIT_DIR = self.root / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
        agent.record_metric_event({"type": "smoke"})
        agent.record_audit_event({"type": "smoke"})
        self.assertEqual(json.loads(agent.METRICS_FILE.read_text())["type"], "smoke")
        self.assertEqual(json.loads(agent.AUDIT_FILE.read_text())["type"], "smoke")


    def test_control_sessions_cli_lists_shows_and_deletes_repo_scoped_sessions(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            repo = Path(tmp) / "repo"
            repo.mkdir()
            session_dir = data_dir / "control-sessions"
            session_dir.mkdir(parents=True, mode=0o700)
            session_id = "cs-1234567890abcdef"
            session_path = session_dir / f"{session_id}.json"
            session_payload = {
                "schema_version": 1,
                "session_id": session_id,
                "repository": str(repo.resolve()),
                "created_at": "2026-09-06T00:00:00Z",
                "updated_at": "2026-09-06T00:01:00Z",
                "turns": [
                    {
                        "control_run_id": "cr-1234567890abcdef",
                        "mode": "plan",
                        "status": "succeeded",
                        "task": "bounded session task",
                        "assistant": "bounded answer",
                        "created_at": "2026-09-06T00:00:00Z",
                        "finished_at": "2026-09-06T00:01:00Z",
                    }
                ],
            }
            session_path.write_text(json.dumps(session_payload), encoding="utf-8")
            session_path.chmod(0o600)
            env = {**os.environ, "LAI_DATA_DIR": str(data_dir)}

            listed = subprocess.run(
                [str(SOURCE), "--sessions", "--json"],
                cwd=repo,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            listed_payload = json.loads(listed.stdout)
            self.assertEqual(listed_payload["sessions"][0]["session_id"], session_id)
            self.assertNotIn("turns", listed_payload["sessions"][0])

            limited_default = subprocess.run(
                [str(SOURCE), "--sessions", "--limit", "1", "--json"],
                cwd=repo,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(
                json.loads(limited_default.stdout)["sessions"][0]["session_id"],
                session_id,
            )

            limited_explicit = subprocess.run(
                [str(SOURCE), "--sessions", "list", "--limit", "1", "--json"],
                cwd=repo,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(
                json.loads(limited_explicit.stdout)["sessions"][0]["session_id"],
                session_id,
            )

            shown = subprocess.run(
                [str(SOURCE), "--sessions", "show", session_id],
                cwd=repo,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("# lai session show", shown.stdout)
            self.assertIn(session_id, shown.stdout)
            self.assertIn("cr-1234567890abcdef", shown.stdout)

            deleted = subprocess.run(
                [str(SOURCE), "--sessions", "delete", session_id, "--json"],
                cwd=repo,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            deleted_payload = json.loads(deleted.stdout)
            self.assertTrue(deleted_payload["session"]["deleted"])
            self.assertEqual(deleted_payload["session"]["session_id"], session_id)
            self.assertFalse(session_path.exists())

            missing = subprocess.run(
                [str(SOURCE), "--sessions", "show", session_id],
                cwd=repo,
                env=env,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("Control session not found", missing.stderr)


    def test_run_history_public_record_keeps_control_run_id_alias(self):
        record = agent.run_history_public_record({
            "run_id": "cr-1234567890abcdef",
            "mode": "plan",
            "status": "succeeded",
        })
        self.assertEqual(record["run_id"], "cr-1234567890abcdef")
        self.assertEqual(record["control_run_id"], "cr-1234567890abcdef")

    def test_run_history_lists_shows_tails_and_exports_recorded_runs(self):
        data_dir = self.base / "data"
        metrics_dir = data_dir / "metrics"
        audit_dir = data_dir / "audit"
        metrics_dir.mkdir(parents=True)
        audit_dir.mkdir(parents=True)
        repo = str(self.root.resolve())

        metric_events = [
            {
                "ts": "2026-09-04T08:00:00Z",
                "run_id": "run-1",
                "repo": repo,
                "mode": "implement",
                "type": "run_start",
                "task_chars": 12,
            },
            {
                "ts": "2026-09-04T08:00:01Z",
                "run_id": "run-1",
                "repo": repo,
                "mode": "implement",
                "type": "api",
                "prompt_tokens": 100,
                "completion_tokens": 20,
                "duration_ms": 2500,
            },
            {
                "ts": "2026-09-04T08:00:02Z",
                "run_id": "run-1",
                "repo": repo,
                "mode": "implement",
                "type": "tool",
                "name": "bash",
                "duration_ms": 300,
            },
            {
                "ts": "2026-09-04T08:01:00Z",
                "run_id": "run-2",
                "repo": repo,
                "mode": "fix",
                "type": "run_start",
                "task_chars": 20,
            },
            {
                "ts": "2026-09-04T08:01:01Z",
                "run_id": "run-2",
                "repo": repo,
                "mode": "fix",
                "type": "tool",
                "name": "patch",
                "duration_ms": 600,
            },
        ]
        audit_events = [
            {
                "ts": "2026-09-04T08:00:03Z",
                "run_id": "run-1",
                "repo": repo,
                "mode": "implement",
                "type": "policy_decision",
                "tool": "bash",
                "decision": "ASK",
                "reason": "git commit requires human action",
            },
            {
                "ts": "2026-09-04T08:00:04Z",
                "run_id": "run-1",
                "repo": repo,
                "mode": "implement",
                "type": "validation",
                "command": "make check",
                "result": "OK",
            },
            {
                "ts": "2026-09-04T08:00:05Z",
                "run_id": "run-1",
                "repo": repo,
                "mode": "implement",
                "type": "checkpoint",
                "phase": "completed",
                "terminal": True,
            },
            {
                "ts": "2026-09-04T08:01:02Z",
                "run_id": "run-2",
                "repo": repo,
                "mode": "fix",
                "type": "patch",
                "paths": ["src/app.py"],
                "result": "OK: patched src/app.py",
            },
            {
                "ts": "2026-09-04T08:01:03Z",
                "run_id": "run-2",
                "repo": repo,
                "mode": "fix",
                "type": "validation",
                "command": "python3 -m pytest -q",
                "result": "FAILED: assertion error in test_app",
            },
            {
                "ts": "2026-09-04T08:01:04Z",
                "run_id": "run-2",
                "repo": repo,
                "mode": "fix",
                "type": "checkpoint",
                "phase": "failed",
                "reason": "SystemExit:1",
                "terminal": True,
            },
        ]
        (metrics_dir / "events.jsonl").write_text(
            "\n".join(json.dumps(item) for item in metric_events) + "\n"
        )
        (audit_dir / "events.jsonl").write_text(
            "\n".join(json.dumps(item) for item in audit_events) + "\n"
        )
        env = {**os.environ, "LAI_DATA_DIR": str(data_dir)}

        listed = subprocess.run(
            [str(SOURCE), "--runs"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("# lai run history", listed.stdout)
        self.assertIn("run-1", listed.stdout)
        self.assertIn("run-2", listed.stdout)
        self.assertIn("mode=implement", listed.stdout)
        self.assertIn("tools=1", listed.stdout)
        self.assertIn("failure=yes", listed.stdout)
        self.assertIn("policy=[ASK:1]", listed.stdout)

        shown = subprocess.run(
            [str(SOURCE), "--run", "show", "run-1"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("# lai run show", shown.stdout)
        self.assertIn("Run ID: run-1", shown.stdout)
        self.assertIn("api_calls: 1", shown.stdout)
        self.assertIn("- bash: 1", shown.stdout)
        self.assertIn("- ASK: 1", shown.stdout)
        self.assertIn("## Validation timeline", shown.stdout)
        self.assertIn("status=pass", shown.stdout)

        latest = subprocess.run(
            [str(SOURCE), "--run", "last"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("Run ID: run-2", latest.stdout)
        self.assertIn("## Last failure or stop reason", latest.stdout)
        self.assertIn("type=checkpoint", latest.stdout)
        self.assertIn("src/app.py", latest.stdout)
        self.assertIn("status=fail", latest.stdout)

        shown_last = subprocess.run(
            [str(SOURCE), "--run", "show", "--last", "--json"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        last_payload = json.loads(shown_last.stdout)
        self.assertEqual(last_payload["run"]["run_id"], "run-2")
        self.assertEqual(last_payload["run"]["last_validation"]["status"], "fail")
        self.assertEqual(last_payload["run"]["last_failure"]["type"], "checkpoint")

        tailed = subprocess.run(
            [str(SOURCE), "--run", "tail", "--last", "--limit", "2"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("# lai run tail", tailed.stdout)
        self.assertIn("Run ID: run-2", tailed.stdout)
        self.assertIn("audit:validation", tailed.stdout)
        self.assertIn("audit:checkpoint", tailed.stdout)

        raw = subprocess.run(
            [str(SOURCE), "--runs", "--json"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(raw.stdout)
        self.assertEqual(payload["version"], agent.VERSION)
        self.assertEqual(payload["runs"][0]["run_id"], "run-1")
        self.assertEqual(payload["runs"][1]["run_id"], "run-2")
        self.assertIsNotNone(payload["runs"][1]["last_failure"])

        export_dir = self.base / "exports"
        exported = subprocess.run(
            [str(SOURCE), "--run", "export", "--last", "--out", str(export_dir)],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("# lai run export", exported.stdout)
        self.assertIn("Run ID: run-2", exported.stdout)
        bundle = export_dir / "lai-run-run-2"
        self.assertTrue((bundle / "summary.json").is_file())
        self.assertTrue((bundle / "timeline.jsonl").is_file())
        self.assertTrue((bundle / "report.md").is_file())
        summary = json.loads((bundle / "summary.json").read_text())
        self.assertTrue(summary["sanitized"])
        self.assertEqual(summary["run_id"], "run-2")
        self.assertEqual(summary["run"]["last_failure"]["type"], "checkpoint")
        timeline = (bundle / "timeline.jsonl").read_text()
        self.assertIn('"type": "validation"', timeline)
        self.assertIn('"validation_status": "fail"', timeline)
        self.assertNotIn('"args"', timeline)
        self.assertNotIn('"answer"', timeline)
        self.assertNotIn("FAILED: assertion error in test_app" * 3, timeline)

        export_json = subprocess.run(
            [str(SOURCE), "--run", "export", "run-1", "--out", str(export_dir), "--json"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        export_payload = json.loads(export_json.stdout)
        self.assertEqual(export_payload["run_id"], "run-1")
        self.assertEqual(export_payload["files"], ["report.md", "summary.json", "timeline.jsonl"])

        missing = subprocess.run(
            [str(SOURCE), "--run", "show", "missing-run"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("Run not found", missing.stderr)

        empty_data = self.base / "empty-data"
        empty_env = {**os.environ, "LAI_DATA_DIR": str(empty_data)}
        empty_last = subprocess.run(
            [str(SOURCE), "--run", "last"],
            cwd=self.root,
            env=empty_env,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(empty_last.returncode, 0)
        self.assertIn("No runs recorded", empty_last.stderr)

    def test_readiness_reports_repository_health_without_model(self):
        original_skills_dir = agent.SKILLS_DIR
        original_metrics_dir = agent.METRICS_DIR
        original_metrics_file = agent.METRICS_FILE
        original_audit_dir = agent.AUDIT_DIR
        original_audit_file = agent.AUDIT_FILE
        try:
            agent.SKILLS_DIR = Path(__file__).parents[1] / ".agents" / "skills"
            agent.METRICS_DIR = self.base / "data" / "metrics"
            agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
            agent.AUDIT_DIR = self.base / "data" / "audit"
            agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
            with mock.patch.object(agent, "gateway", return_value="127.0.0.1"), \
                 mock.patch.object(agent, "doctor_status", return_value=(401, 200)):
                rendered = agent.render_readiness_status()
                raw = agent.render_readiness_status(json_mode=True)
        finally:
            agent.SKILLS_DIR = original_skills_dir
            agent.METRICS_DIR = original_metrics_dir
            agent.METRICS_FILE = original_metrics_file
            agent.AUDIT_DIR = original_audit_dir
            agent.AUDIT_FILE = original_audit_file

        self.assertIn("# lai readiness", rendered)
        self.assertIn("Authentication: OK", rendered)
        self.assertIn("mode_skills", rendered)
        payload = json.loads(raw)
        self.assertEqual(payload["version"], agent.VERSION)
        self.assertTrue(payload["server"]["authentication_ok"])
        self.assertIn(payload["overall"], {"ready", "attention"})
        self.assertTrue(
            any(item["mode"] == "diagnose" for item in payload["skills"])
        )
        self.assertTrue(
            any(item["mode"] == "ci-fix" for item in payload["skills"])
        )
        self.assertTrue(
            any(item["mode"] == "release" for item in payload["skills"])
        )

    def test_release_preflight_context_prefers_project_commands(self):
        original_skills_dir = agent.SKILLS_DIR
        original_metrics_dir = agent.METRICS_DIR
        original_metrics_file = agent.METRICS_FILE
        original_audit_dir = agent.AUDIT_DIR
        original_audit_file = agent.AUDIT_FILE
        try:
            (self.root / "Makefile").write_text(
                "check:\n\ttrue\n"
                "test-dev:\n\t.venv/bin/python -m pytest -q\n"
                "test:\n\tpython3 -m unittest discover -s tests -v\n"
                "validate:\n\t./scripts/validate.sh\n"
                "milestone-gate: test-dev validate\n"
            )
            agent.SKILLS_DIR = Path(__file__).parents[1] / ".agents" / "skills"
            agent.METRICS_DIR = self.base / "data" / "metrics"
            agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
            agent.AUDIT_DIR = self.base / "data" / "audit"
            agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
            with mock.patch.object(agent, "gateway", return_value="127.0.0.1"), \
                 mock.patch.object(agent, "doctor_status", return_value=(401, 200)):
                context = agent.render_release_preflight_context()
        finally:
            agent.SKILLS_DIR = original_skills_dir
            agent.METRICS_DIR = original_metrics_dir
            agent.METRICS_FILE = original_metrics_file
            agent.AUDIT_DIR = original_audit_dir
            agent.AUDIT_FILE = original_audit_file

        self.assertIn("RELEASE PREFLIGHT", context)
        self.assertIn(f"Version: {agent.VERSION}", context)
        self.assertIn("Readiness overall:", context)
        self.assertIn("- make milestone-gate", context)
        self.assertNotIn("- make check\n", context)
        self.assertNotIn("- make test-dev\n", context)
        self.assertNotIn("- make test\n", context)
        self.assertNotIn("- make validate\n", context)
        self.assertIn("Do not probe ad-hoc pytest/python commands", context)

    def test_release_check_is_deterministic_and_read_only(self):
        data_dir = self.base / "data"
        env = {**os.environ, "LAI_DATA_DIR": str(data_dir)}
        (self.root / "Makefile").write_text(
            "check:\n\ttrue\n"
            "test-dev:\n\t.venv/bin/python -m pytest -q\n"
            "test:\n\tpython3 -m unittest discover -s tests -v\n"
            "validate:\n\t./scripts/validate.sh\n"
        )
        subprocess.run(["git", "add", "Makefile"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-m",
                "add Makefile",
            ],
            cwd=self.root,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        result = subprocess.run(
            [str(SOURCE), "--release-check", "--target", agent.VERSION, "--json"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], agent.VERSION)
        self.assertEqual(payload["expected_tag"], f"v{agent.VERSION}")
        self.assertEqual(payload["release_channel"], "stable")
        self.assertFalse(payload["expected_prerelease"])
        self.assertIn(payload["phase"], {"ready_for_integration", "ready_to_tag", "released", "blocked", "attention"})
        self.assertIn("make validate", payload["validation_commands"])
        self.assertTrue(
            any(item["name"] == "release_safety" for item in payload["checks"])
        )

        rendered = subprocess.run(
            [str(SOURCE), "--release-check"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
            check=True,
        )
        self.assertIn("# lai release check", rendered.stdout)
        self.assertIn("Release check is read-only", rendered.stdout)

    def test_release_check_distinguishes_integration_and_tag_safety(self):
        readiness = {
            "git": {
                "branch": "feature/release-state",
                "clean": True,
                "status": "[clean]",
                "origin": "git@github.com:fenatodev/lai-harness.git",
            },
            "overall": "ready",
        }

        expected_tag = f"v{agent.VERSION}"
        state = {
            "head": "aaa111",
            "origin_main": "bbb222",
            "exact_tag": "[none]",
            "latest_tag": "v0.4.0-beta.9",
            "tag_target": "[none]",
        }

        def fake_git(args, default="[unavailable]", timeout=10):
            if args == ["rev-parse", "HEAD"]:
                return state["head"]
            if args == ["rev-parse", "origin/main"]:
                return state["origin_main"]
            if args == ["describe", "--tags", "--exact-match", "HEAD"]:
                return state["exact_tag"]
            if args == ["describe", "--tags", "--abbrev=0"]:
                return state["latest_tag"]
            if args == ["rev-parse", f"{expected_tag}^{{}}"]:
                return state["tag_target"]
            return default

        with mock.patch.object(agent, "collect_readiness_status", return_value=readiness), \
                mock.patch.object(agent, "git_command_text", side_effect=fake_git), \
                mock.patch.object(agent, "release_validation_commands", return_value=["make validate"]):
            candidate = agent.collect_release_check(agent.VERSION)
            self.assertEqual(candidate["phase"], "ready_for_integration")
            self.assertFalse(candidate["tag_ready"])

            readiness["git"]["branch"] = "main"
            state["origin_main"] = state["head"]
            taggable = agent.collect_release_check(agent.VERSION)
            self.assertEqual(taggable["phase"], "ready_to_tag")
            self.assertTrue(taggable["tag_ready"])
            self.assertEqual(taggable["origin_main"], state["head"])

            state["origin_main"] = "different333"
            divergent = agent.collect_release_check(agent.VERSION)
            self.assertEqual(divergent["overall"], "blocked")
            self.assertEqual(divergent["phase"], "blocked")
            self.assertFalse(divergent["tag_ready"])

            state["origin_main"] = state["head"]
            state["tag_target"] = "old444"
            wrong_tag = agent.collect_release_check(agent.VERSION)
            self.assertEqual(wrong_tag["overall"], "blocked")
            self.assertEqual(wrong_tag["phase"], "blocked")
            self.assertIn("old444", next(
                item["detail"] for item in wrong_tag["checks"] if item["name"] == "tag_state"
            ))

            state["tag_target"] = state["head"]
            state["exact_tag"] = expected_tag
            released = agent.collect_release_check(agent.VERSION)
            self.assertEqual(released["overall"], "ready")
            self.assertEqual(released["phase"], "released")
            self.assertFalse(released["tag_ready"])

    def test_release_channel_distinguishes_prerelease_and_stable_targets(self):
        for version in ("0.4.0-alpha.1", "0.4.0-beta.24", "0.4.0-rc.1"):
            self.assertTrue(agent.release_is_prerelease(version), version)
            self.assertEqual(agent.release_channel(version), "prerelease")
        for version in ("0.4.0", "v0.4.0", "0.4.0+build.7"):
            self.assertFalse(agent.release_is_prerelease(version), version)
            self.assertEqual(agent.release_channel(version), "stable")

    def test_release_pack_writes_local_files_without_repo_mutation(self):
        data_dir = self.base / "data"
        env = {**os.environ, "LAI_DATA_DIR": str(data_dir)}
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "RELEASE-NOTES.md").write_text(
            "# Release notes\n\n"
            "## lai harness v0.4.0-beta.24 — correct beta title\n\n"
            "ready body for beta pack\n\n"
            "## lai harness v0.4.0-beta.17 — older release\n\n"
            "### Release body for GitHub\n\n"
            "stale body from older beta\n",
            encoding="utf-8",
        )
        (docs / "RELEASE-CHECKLIST.md").write_text("checklist\n", encoding="utf-8")
        (docs / "GITHUB-PUBLISHING.md").write_text("publishing\n", encoding="utf-8")
        (self.root / "Makefile").write_text("validate:\n\ttrue\n")
        subprocess.run(["git", "add", "docs", "Makefile"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c", "user.name=Test",
                "-c", "user.email=test@example.invalid",
                "commit", "-q", "-m", "release docs",
            ],
            cwd=self.root,
            check=True,
        )

        out_dir = self.base / "pack"
        result = subprocess.run(
            [
                str(SOURCE),
                "--release-pack",
                "--target",
                "0.4.0-beta.24",
                "--out",
                str(out_dir),
                "--json",
            ],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], agent.VERSION)
        self.assertEqual(payload["expected_tag"], "v0.4.0-beta.24")
        self.assertEqual(payload["release_channel"], "prerelease")
        self.assertTrue(payload["expected_prerelease"])
        self.assertEqual(payload["pack_dir"], str(out_dir.resolve()))
        self.assertEqual(payload["repository"], "<repo-checkout>")
        self.assertFalse(payload["with_vsix"])
        for key in ("summary", "release_body", "checklist", "publishing", "commands"):
            self.assertTrue(Path(payload["files"][key]).is_file(), key)
        release_body = (out_dir / "release-body.md").read_text()
        self.assertIn("## lai harness v0.4.0-beta.24 — correct beta title", release_body)
        self.assertIn("ready body for beta pack", release_body)
        self.assertNotIn("stale body from older beta", release_body)
        commands = (out_dir / "human-release-commands.sh").read_text()
        summary = (out_dir / "summary.json").read_text()
        self.assertIn("cd /path/to/lai-harness-checkout", commands)
        self.assertNotIn(str(self.root), commands)
        self.assertNotIn(str(self.root), summary)
        self.assertIn("git tag -a v0.4.0-beta.24", commands)
        self.assertIn("v0.4.0-beta.24 — correct beta title", commands)
        self.assertNotIn("remote capability profiles", commands)
        self.assertIn("git pull --ff-only origin main", commands)
        self.assertIn("git push origin v0.4.0-beta.24", commands)
        self.assertNotIn("git merge --ff-only", commands)
        self.assertNotIn("git push --atomic origin main", commands)
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(status.stdout.strip(), "")

        bad = subprocess.run(
            [
                str(SOURCE),
                "--release-pack",
                "--target",
                "0.4.0-beta.24",
                "--out",
                str(self.root / "release-pack"),
            ],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
        )
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("inside the repository", bad.stderr)

    def test_release_pack_target_section_is_exact_and_fallback_is_neutral(self):
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "RELEASE-NOTES.md").write_text(
            "## lai harness v0.4.0-beta.10 — ten\n\nten body\n\n"
            "## lai harness v0.4.0-beta.1 — one\n\none body\n\n"
            "## lai harness v0.4.0-beta.0 — legacy\n\n"
            "### Release body for GitHub\n\nstale legacy body\n",
            encoding="utf-8",
        )

        section = agent.release_pack_notes_section("0.4.0-beta.1")
        self.assertIn("v0.4.0-beta.1 — one", section)
        self.assertIn("one body", section)
        self.assertNotIn("beta.10", section)
        self.assertNotIn("stale legacy body", section)
        self.assertEqual(
            agent.release_pack_title("0.4.0-beta.1"),
            "v0.4.0-beta.1 — one",
        )

        fallback = agent.release_pack_body("0.4.0-beta.999", "v0.4.0-beta.999")
        self.assertIn("v0.4.0-beta.999 is a pre-release", fallback)
        self.assertIn("experimental", fallback)
        self.assertNotIn("ten body", fallback)
        self.assertNotIn("stale legacy body", fallback)
        self.assertEqual(
            agent.release_pack_title("0.4.0-beta.999"),
            "v0.4.0-beta.999 — lai harness release",
        )

        stable = agent.release_pack_body("0.4.0", "v0.4.0")
        self.assertIn("v0.4.0 is a stable release", stable)
        self.assertIn("local-first and auditable", stable)
        self.assertNotIn("experimental", stable)
        self.assertNotIn("beta release", stable)

    def test_release_governance_reports_manual_publication_actions(self):
        data_dir = self.base / "data"
        env = {**os.environ, "LAI_DATA_DIR": str(data_dir)}
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "RELEASE-NOTES.md").write_text(
            "# Release notes\n\n"
            "### Release body for GitHub\n\n"
            "ready body for governance\n",
            encoding="utf-8",
        )
        (docs / "RELEASE-CHECKLIST.md").write_text("checklist\n", encoding="utf-8")
        (docs / "GITHUB-PUBLISHING.md").write_text("publishing\n", encoding="utf-8")
        (self.root / "Makefile").write_text("validate:\n\ttrue\n")
        subprocess.run(["git", "add", "docs", "Makefile"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c", "user.name=Test",
                "-c", "user.email=test@example.invalid",
                "commit", "-q", "-m", "release docs",
            ],
            cwd=self.root,
            check=True,
        )

        out_dir = self.base / "governance-pack"
        subprocess.run(
            [
                str(SOURCE),
                "--release-pack",
                "--target",
                "0.4.0-beta.24",
                "--out",
                str(out_dir),
                "--json",
            ],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=12,
            check=True,
        )

        result = subprocess.run(
            [
                str(SOURCE),
                "--release-governance",
                "--target",
                "0.4.0-beta.24",
                "--json",
            ],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], agent.VERSION)
        self.assertEqual(payload["expected_tag"], "v0.4.0-beta.24")
        self.assertIn(payload["overall"], {"action_required", "blocked"})
        self.assertIn(payload["release_pack"]["status"], {"ok", "warn"})
        action_ids = {item["id"] for item in payload["manual_actions"]}
        self.assertIn("github_branch_protection", action_ids)
        self.assertIn("github_release", action_ids)

        rendered = subprocess.run(
            [str(SOURCE), "--release-governance", "--target", "0.4.0-beta.24"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
            check=True,
        )
        self.assertIn("# lai release governance", rendered.stdout)
        self.assertIn("GitHub branch protection", rendered.stdout)
        self.assertIn("read-only", rendered.stdout)

        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(status.stdout.strip(), "")

    def test_release_governance_parses_remote_and_github_origins(self):
        options = agent.parse_release_governance_args([
            "--target", "0.4.0-beta.24", "--remote", "--json",
        ])
        self.assertEqual(options["target"], "0.4.0-beta.24")
        self.assertTrue(options["remote"])
        self.assertTrue(options["json"])
        self.assertEqual(
            agent.github_repository_slug("git@github.com:fenatodev/lai-harness.git"),
            "fenatodev/lai-harness",
        )
        self.assertEqual(
            agent.github_repository_slug("https://github.com/fenatodev/lai-harness.git"),
            "fenatodev/lai-harness",
        )
        self.assertIsNone(agent.github_repository_slug("git@example.invalid:owner/repo.git"))

    def test_remote_branch_protection_verifies_beta_policy(self):
        remote = {
            "required_status_checks": {
                "strict": True,
                "contexts": list(agent.GITHUB_REQUIRED_STATUS_CHECKS),
            },
            "required_pull_request_reviews": {"required_approving_review_count": 1},
            "required_linear_history": {"enabled": True},
            "enforce_admins": {"enabled": True},
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
        }
        with mock.patch.object(
            agent,
            "github_api_get",
            return_value={"ok": True, "status": 200, "data": remote, "error": ""},
        ):
            result = agent.github_branch_protection_status("fenatodev/lai-harness", token="secret")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(all(result["requirements"].values()))
        self.assertEqual(
            set(result["observed_checks"]),
            set(agent.GITHUB_REQUIRED_STATUS_CHECKS),
        )

    def test_remote_release_verifies_optional_vsix_digest(self):
        vsix = self.base / "lai-harness-0.4.0-beta.24.vsix"
        vsix.write_bytes(b"inspected-vsix")
        digest = agent.file_sha256(vsix)
        remote = {
            "tag_name": "v0.4.0-beta.24",
            "draft": False,
            "prerelease": True,
            "html_url": "https://github.com/fenatodev/lai-harness/releases/tag/v0.4.0-beta.24",
            "assets": [{
                "name": vsix.name,
                "digest": f"sha256:{digest}",
            }],
        }
        pack = {"vsix": {"path": str(vsix), "present": True, "optional": True}}
        with mock.patch.object(
            agent,
            "github_api_get",
            return_value={"ok": True, "status": 200, "data": remote, "error": ""},
        ):
            result = agent.github_release_status(
                "fenatodev/lai-harness",
                "v0.4.0-beta.24",
                pack,
                token="secret",
            )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["asset"]["status"], "ok")
        self.assertTrue(result["asset"]["digest_match"])

    def test_remote_release_requires_channel_matching_prerelease_flag(self):
        vsix = self.base / "lai-harness-0.4.0.vsix"
        vsix.write_bytes(b"stable-vsix")
        digest = agent.file_sha256(vsix)
        pack = {"vsix": {"path": str(vsix), "present": True, "optional": True}}
        stable = {
            "tag_name": "v0.4.0",
            "draft": False,
            "prerelease": False,
            "html_url": "https://github.com/fenatodev/lai-harness/releases/tag/v0.4.0",
            "assets": [{"name": vsix.name, "digest": f"sha256:{digest}"}],
        }
        with mock.patch.object(
            agent,
            "github_api_get",
            return_value={"ok": True, "status": 200, "data": stable, "error": ""},
        ):
            result = agent.github_release_status(
                "fenatodev/lai-harness",
                "v0.4.0",
                pack,
                token="secret",
                target_version="0.4.0",
            )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["release_channel"], "stable")
        self.assertFalse(result["expected_prerelease"])
        self.assertTrue(result["asset"]["digest_match"])
        self.assertIn("stable release", result["detail"])

        wrong = dict(stable, prerelease=True)
        with mock.patch.object(
            agent,
            "github_api_get",
            return_value={"ok": True, "status": 200, "data": wrong, "error": ""},
        ):
            mismatch = agent.github_release_status(
                "fenatodev/lai-harness",
                "v0.4.0",
                pack,
                token="secret",
                target_version="0.4.0",
            )
        self.assertEqual(mismatch["status"], "warn")
        self.assertIn("prerelease=false", mismatch["detail"])

        bad_digest = dict(
            stable,
            assets=[{"name": vsix.name, "digest": "sha256:" + "0" * 64}],
        )
        with mock.patch.object(
            agent,
            "github_api_get",
            return_value={"ok": True, "status": 200, "data": bad_digest, "error": ""},
        ):
            digest_mismatch = agent.github_release_status(
                "fenatodev/lai-harness",
                "v0.4.0",
                pack,
                token="secret",
                target_version="0.4.0",
            )
        self.assertEqual(digest_mismatch["status"], "fail")
        self.assertFalse(digest_mismatch["asset"]["digest_match"])

    def test_release_governance_manual_action_respects_stable_channel(self):
        payload = {"target_version": "0.4.0", "expected_tag": "v0.4.0"}
        pack = {"status": "ok"}
        actions = agent.release_governance_manual_actions(payload, pack)
        release = next(item for item in actions if item["id"] == "github_release")
        self.assertIn("stable release", release["title"])
        self.assertIn("pre-release flag disabled", release["detail"])

    def test_remote_governance_clears_verified_github_actions(self):
        release_payload = {
            "overall": "ready",
            "phase": "released",
            "target_version": "0.4.0-beta.24",
            "expected_tag": "v0.4.0-beta.24",
            "branch": "main",
            "head": "abc123",
            "latest_tag": "v0.4.0-beta.24",
            "exact_tag": "v0.4.0-beta.24",
            "origin": "git@github.com:fenatodev/lai-harness.git",
        }
        pack = {
            "status": "ok",
            "detail": "required release pack files are present",
            "pack_dir": "/tmp/pack",
            "present": [],
            "missing": [],
            "required_files": {},
            "vsix": {"path": "/tmp/pack/lai-harness-0.4.0-beta.24.vsix", "present": False, "optional": True},
        }
        remote = {
            "enabled": True,
            "repository": "fenatodev/lai-harness",
            "authenticated": True,
            "credential_source": "git-credential",
            "branch_protection": {"status": "ok", "detail": "verified"},
            "release": {"status": "ok", "detail": "verified"},
        }
        with mock.patch.object(agent, "collect_release_check", return_value=release_payload), \
                mock.patch.object(agent, "release_governance_pack_status", return_value=pack), \
                mock.patch.object(agent, "collect_github_release_governance", return_value=remote):
            result = agent.collect_release_governance(target="0.4.0-beta.24", remote=True)
        self.assertEqual(result["overall"], "ready")
        self.assertEqual(result["manual_actions"], [])
        checks = {item["name"]: item["status"] for item in result["checks"]}
        self.assertEqual(checks["github_branch_protection"], "ok")
        self.assertEqual(checks["github_release"], "ok")

    def test_remote_governance_keeps_unverified_action(self):
        release_payload = {
            "overall": "ready",
            "phase": "released",
            "target_version": "0.4.0-beta.24",
            "expected_tag": "v0.4.0-beta.24",
            "branch": "main",
            "head": "abc123",
            "latest_tag": "v0.4.0-beta.24",
            "exact_tag": "v0.4.0-beta.24",
            "origin": "git@github.com:fenatodev/lai-harness.git",
        }
        pack = {
            "status": "ok",
            "detail": "required release pack files are present",
            "pack_dir": "/tmp/pack",
            "present": [],
            "missing": [],
            "required_files": {},
            "vsix": {"path": "/tmp/missing.vsix", "present": False, "optional": True},
        }
        remote = {
            "enabled": True,
            "repository": "fenatodev/lai-harness",
            "authenticated": False,
            "credential_source": "none",
            "branch_protection": {"status": "unverified", "detail": "credential required"},
            "release": {"status": "ok", "detail": "verified"},
        }
        with mock.patch.object(agent, "collect_release_check", return_value=release_payload), \
                mock.patch.object(agent, "release_governance_pack_status", return_value=pack), \
                mock.patch.object(agent, "collect_github_release_governance", return_value=remote):
            result = agent.collect_release_governance(target="0.4.0-beta.24", remote=True)
        self.assertEqual(result["overall"], "action_required")
        self.assertEqual(
            [item["id"] for item in result["manual_actions"]],
            ["github_branch_protection"],
        )

    def test_project_handoff_remote_converges_live_release_state(self):
        options = agent.parse_project_handoff_args([
            "--target", "0.4.0-beta.24", "--remote", "--json",
        ])
        self.assertTrue(options["remote"])
        self.assertTrue(options["json"])

        release_payload = {
            "target_version": "0.4.0-beta.24",
            "expected_tag": "v0.4.0-beta.24",
            "branch": "main",
            "head": "abc123",
            "latest_tag": "v0.4.0-beta.24",
            "exact_tag": "v0.4.0-beta.24",
            "overall": "ready",
            "phase": "released",
        }
        pack = {
            "status": "ok",
            "pack_dir": "/tmp/lai-harness-release-pack-v0.4.0-beta.24",
            "vsix": {"path": "/tmp/lai-harness-0.4.0-beta.24.vsix", "present": True},
        }
        local_governance = {
            "overall": "action_required",
            "release_pack": pack,
            "manual_actions": [{"id": "github_release", "title": "Verify release", "detail": "remote not checked"}],
            "remote": {"enabled": False},
        }
        remote_state = {
            "enabled": True,
            "repository": "fenatodev/lai-harness",
            "authenticated": True,
            "credential_source": "git-credential",
            "branch_protection": {"status": "ok", "detail": "verified"},
            "release": {
                "status": "ok",
                "detail": "published pre-release verified",
                "asset": {
                    "digest_match": True,
                    "local_sha256": "abc",
                    "remote_digest": "sha256:abc",
                },
            },
        }
        remote_governance = {
            "overall": "ready",
            "release_pack": pack,
            "manual_actions": [],
            "remote": remote_state,
        }

        def governance(target=None, remote=False):
            return remote_governance if remote else local_governance

        with mock.patch.object(agent, "collect_release_check", return_value=release_payload), \
                mock.patch.object(agent, "collect_release_governance", side_effect=governance) as collect_governance, \
                mock.patch.object(agent, "collect_safe_workspace_status", return_value={"base_dir": "/tmp/workspaces", "workspaces": []}), \
                mock.patch.object(agent, "load_active_spec", return_value=None):
            payload = agent.project_handoff_payload("0.4.0-beta.24", remote=True)
        self.assertEqual(payload["release_governance_local_overall"], "action_required")
        self.assertEqual(payload["release_governance_remote_overall"], "ready")
        self.assertEqual(payload["release_governance_overall"], "ready")
        self.assertEqual(payload["manual_actions"], [])
        self.assertTrue(payload["release_governance_remote_enabled"])
        self.assertEqual(payload["release_governance_remote"]["credential_source"], "git-credential")
        self.assertNotIn("token", json.dumps(payload).lower())
        markdown = agent.render_project_handoff_markdown(payload)
        self.assertIn("Remote GitHub evidence", markdown)
        self.assertIn("VSIX digest match: `True`", markdown)
        self.assertIn("project-handoff --target 0.4.0-beta.24 --remote --json", markdown)
        self.assertEqual(
            [call.kwargs["remote"] for call in collect_governance.call_args_list],
            [False, True],
        )

        with mock.patch.object(agent, "collect_release_check", return_value=release_payload), \
                mock.patch.object(agent, "collect_release_governance", return_value=local_governance) as offline_governance, \
                mock.patch.object(agent, "collect_safe_workspace_status", return_value={"base_dir": "/tmp/workspaces", "workspaces": []}), \
                mock.patch.object(agent, "load_active_spec", return_value=None):
            offline = agent.project_handoff_payload("0.4.0-beta.24", remote=False)
        self.assertFalse(offline["release_governance_remote_enabled"])
        self.assertIsNone(offline["release_governance_remote_overall"])
        offline_governance.assert_called_once_with(target="0.4.0-beta.24", remote=False)

    def test_project_handoff_renders_and_writes_next_chat_reference(self):
        data_dir = self.base / "data"
        env = {
            **os.environ,
            "LAI_DATA_DIR": str(data_dir),
            "LAI_HOST": "127.0.0.1",
            "LAI_PORT": "1",
        }
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "RELEASE-NOTES.md").write_text(
            "# Release notes\n\n"
            "### Release body for GitHub\n\n"
            "ready body for project handoff\n",
            encoding="utf-8",
        )
        (docs / "RELEASE-CHECKLIST.md").write_text("checklist\n", encoding="utf-8")
        (docs / "GITHUB-PUBLISHING.md").write_text("publishing\n", encoding="utf-8")
        (self.root / "Makefile").write_text("validate:\n\ttrue\n")
        subprocess.run(["git", "add", "docs", "Makefile"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c", "user.name=Test",
                "-c", "user.email=test@example.invalid",
                "commit", "-q", "-m", "release docs",
            ],
            cwd=self.root,
            check=True,
        )

        rendered = subprocess.run(
            [str(SOURCE), "--project-handoff", "--target", "0.4.0"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
            check=True,
        )
        self.assertIn("# lai harness project handoff", rendered.stdout)
        self.assertIn("Prompt to paste into the next ChatGPT chat", rendered.stdout)
        self.assertIn("Do not run git tag", rendered.stdout)

        out_dir = self.base / "handoff"
        result = subprocess.run(
            [
                str(SOURCE),
                "--project-handoff",
                "--target",
                "0.4.0",
                "--out",
                str(out_dir),
                "--json",
            ],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], agent.VERSION)
        self.assertEqual(payload["expected_tag"], "v0.4.0")
        self.assertEqual(payload["handoff_dir"], str(out_dir.resolve()))
        self.assertTrue(Path(payload["files"]["markdown"]).is_file())
        self.assertTrue(Path(payload["files"]["next_chat_prompt"]).is_file())
        self.assertTrue(Path(payload["files"]["summary"]).is_file())
        self.assertIn("Remote Desktop Commander", Path(payload["files"]["markdown"]).read_text())
        self.assertIn("Repo local", Path(payload["files"]["next_chat_prompt"]).read_text())

        bad = subprocess.run(
            [
                str(SOURCE),
                "--project-handoff",
                "--target",
                "0.4.0",
                "--out",
                str(self.root / "handoff"),
            ],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
        )
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("inside the repository", bad.stderr)

        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(status.stdout.strip(), "")

    def test_deterministic_readiness_cli_needs_no_model(self):
        data_dir = self.base / "data"
        env = {**os.environ, "LAI_DATA_DIR": str(data_dir)}
        result = subprocess.run(
            [str(SOURCE), "--readiness", "--json"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["product"], "lai harness")
        self.assertEqual(payload["version"], agent.VERSION)
        self.assertEqual(payload["repository"], str(self.root.resolve()))
        self.assertIn("checks", payload)

    def test_new_diagnostic_skills_load_from_standard_files(self):
        skills = Path(__file__).parents[1] / ".agents" / "skills"
        self.assertIn("MODE: DIAGNOSE", agent.load_mode_skill("diagnose", skills))
        self.assertIn("MODE: CI-FIX", agent.load_mode_skill("ci-fix", skills))
        self.assertIn("MODE: RELEASE", agent.load_mode_skill("release", skills))

    def test_policy_keeps_diagnose_and_release_read_only_but_allows_ci_fix_writes(self):
        write_args = {"path": "sample.txt", "content": "x"}
        self.assertEqual(
            agent.evaluate_tool_policy("create", write_args, mode="diagnose")["decision"],
            "DENY",
        )
        self.assertEqual(
            agent.evaluate_tool_policy("create", write_args, mode="release")["decision"],
            "DENY",
        )
        with mock.patch.object(agent, "current_policy_git_branch", return_value="feature/test"):
            self.assertEqual(
                agent.evaluate_tool_policy("create", write_args, mode="ci-fix")["decision"],
                "ALLOW",
            )

    def test_policy_blocks_write_tools_on_protected_branches_unless_overridden(self):
        write_args = {"path": "sample.txt", "content": "x"}
        with mock.patch.object(agent, "current_policy_git_branch", return_value="main"):
            policy = agent.evaluate_tool_policy("patch", write_args, mode="implement")
        self.assertEqual(policy["decision"], "DENY")
        self.assertIn("protected branch main", policy["reason"])

        with mock.patch.object(agent, "current_policy_git_branch", return_value="release/0.4"), \
             mock.patch.dict(os.environ, {}, clear=True):
            policy = agent.evaluate_tool_policy("rewrite", write_args, mode="fix")
        self.assertEqual(policy["decision"], "DENY")

        with mock.patch.object(agent, "current_policy_git_branch", return_value="main"), \
             mock.patch.dict(os.environ, {agent.PROTECTED_WRITE_OVERRIDE_ENV: "1"}):
            policy = agent.evaluate_tool_policy("patch", write_args, mode="implement")
        self.assertEqual(policy["decision"], "ALLOW")

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

    def test_audit_prints_policy_and_user_action_lifecycle(self):
        agent.AUDIT_DIR = self.root / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
        agent.record_audit_event({
            "type": "policy_decision",
            "tool": "bash",
            "decision": "ASK",
            "reason": "git commit requires explicit user action",
        })
        agent.record_audit_event({
            "type": "run_outcome",
            "outcome": "user_action_required",
            "tool": "bash",
            "reason": "git commit requires explicit user action",
        })
        output = io.StringIO()
        with redirect_stdout(output):
            agent.print_lai_audit()
        shown = output.getvalue()
        self.assertIn("## Policy decision", shown)
        self.assertIn("Decision: ASK", shown)
        self.assertIn("## Run outcome", shown)
        self.assertIn("Outcome: user_action_required", shown)

    def test_audit_prints_checkpoint_and_recovery_events(self):
        agent.AUDIT_DIR = self.base / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
        agent.record_audit_event({
            "type": "checkpoint", "phase": "tool_completed",
            "terminal": False, "last_tool": "read",
        })
        agent.record_audit_event({
            "type": "recovery_resume", "from_run_id": "old",
            "new_run_id": "new",
        })
        output = io.StringIO()
        with redirect_stdout(output):
            agent.print_lai_audit()
        shown = output.getvalue()
        self.assertIn("## Checkpoint", shown)
        self.assertIn("Phase: tool_completed", shown)
        self.assertIn("## Recovery resume", shown)
        self.assertIn("From run: old", shown)

    def test_patch_dispatch_records_hashes_and_tool_metric(self):
        target = self.root / "sample.txt"
        target.write_text("before")
        agent.METRICS_DIR = self.root / "metrics"
        agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
        agent.AUDIT_DIR = self.root / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"
        with mock.patch.object(agent, "current_policy_git_branch", return_value="feature/test"):
            result = agent.run_tool("patch", {"changes": [
                {"path": "sample.txt", "old": "before", "new": "after"},
            ]})
        self.assertTrue(result.startswith("OK:"))
        audit = json.loads(agent.AUDIT_FILE.read_text())
        self.assertNotEqual(audit["before_hashes"], audit["after_hashes"])
        metric = json.loads(agent.METRICS_FILE.read_text())
        self.assertEqual(metric["name"], "patch")
        self.assertTrue(metric["ok"])


    def test_safe_workspace_create_status_and_clean(self):
        (self.root / "sample.txt").write_text("sample\n")
        subprocess.run(["git", "add", "sample.txt"], cwd=self.root, check=True)
        subprocess.run(
            [
                "git",
                "-c", "user.name=Test",
                "-c", "user.email=test@example.invalid",
                "commit", "-q", "-m", "seed",
            ],
            cwd=self.root,
            check=True,
        )

        base = self.base / "safe-workspaces"
        with mock.patch.dict(os.environ, {agent.SAFE_WORKSPACE_BASE_ENV: str(base)}):
            created = json.loads(agent.handle_safe_workspace([
                "create", "--name", "demo", "--json",
            ]))
            target = Path(created["path"])
            self.assertEqual(created["status"], "created")
            self.assertEqual(created["branch"], agent.SAFE_WORKSPACE_BRANCH)
            self.assertTrue((target / "sample.txt").is_file())
            self.assertTrue((target / agent.SAFE_WORKSPACE_METADATA).is_file())
            self.assertEqual(
                agent.workspace_git_text(target, ["branch", "--show-current"]),
                agent.SAFE_WORKSPACE_BRANCH,
            )

            status = json.loads(agent.handle_safe_workspace(["status", "--json"]))
            self.assertEqual(status["workspaces"][0]["name"], "demo")

            cleaned = json.loads(agent.handle_safe_workspace([
                "clean", "demo", "--json",
            ]))
            self.assertEqual(cleaned["status"], "cleaned")
            self.assertFalse(target.exists())

    def test_safe_workspace_clean_refuses_outside_path(self):
        base = self.base / "safe-workspaces"
        outside = self.base / "outside"
        outside.mkdir()
        with mock.patch.dict(os.environ, {agent.SAFE_WORKSPACE_BASE_ENV: str(base)}):
            with self.assertRaisesRegex(SystemExit, "inside safe workspace base"):
                agent.handle_safe_workspace(["clean", str(outside)])

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

    def test_checkpoint_storage_refuses_repository_directory(self):
        original = agent.STATE_BASE
        try:
            agent.STATE_BASE = self.root / ".lai-data" / "state"
            with self.assertRaisesRegex(RuntimeError, "outside repository"):
                agent.run_checkpoint_path()
        finally:
            agent.STATE_BASE = original

    def test_run_checkpoint_atomic_round_trip(self):
        sample = self.root / "sample.txt"
        sample.write_text("alpha\n")
        checkpoint = agent.build_run_checkpoint(
            mode="fix",
            task="repair sample",
            phase="started",
            tracked_paths=["sample.txt"],
        )
        path = agent.save_run_checkpoint(checkpoint)
        loaded = agent.load_run_checkpoint()
        self.assertEqual(loaded["schema_version"], 1)
        self.assertEqual(loaded["phase"], "started")
        self.assertEqual(loaded["tracked_hashes"], checkpoint["tracked_hashes"])
        self.assertEqual(path.parent, self.base / "data" / "checkpoints")

    def test_run_checkpoint_atomic_failure_preserves_previous_file(self):
        first = agent.build_run_checkpoint(mode="fix", task="one", phase="started")
        path = agent.save_run_checkpoint(first)
        before = path.read_text()
        second = agent.build_run_checkpoint(mode="fix", task="two", phase="tool_completed")
        with mock.patch.object(agent.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaisesRegex(OSError, "replace failed"):
                agent.save_run_checkpoint(second)
        self.assertEqual(path.read_text(), before)

    def test_recovery_compatibility_detects_branch_status_and_hash_drift(self):
        sample = self.root / "sample.txt"
        sample.write_text("alpha\n")
        checkpoint = agent.build_run_checkpoint(
            mode="general", task="continue", phase="tool_completed",
            tracked_paths=["sample.txt"],
        )
        compatible, reasons = agent.check_recovery_compatibility(checkpoint)
        self.assertTrue(compatible, reasons)
        sample.write_text("changed\n")
        compatible, reasons = agent.check_recovery_compatibility(checkpoint)
        self.assertFalse(compatible)
        self.assertTrue(any("hash changed" in reason for reason in reasons))

    def test_recovery_compatibility_detects_branch_and_status_drift(self):
        checkpoint = agent.build_run_checkpoint(
            mode="general", task="continue", phase="started",
        )
        with mock.patch.object(agent, "workspace_git_branch", return_value="other"):
            compatible, reasons = agent.check_recovery_compatibility(checkpoint)
        self.assertFalse(compatible)
        self.assertTrue(any("branch changed" in reason for reason in reasons))

        extra = self.root / "extra.txt"
        extra.write_text("new\n")
        compatible, reasons = agent.check_recovery_compatibility(checkpoint)
        self.assertFalse(compatible)
        self.assertIn("Git status changed since checkpoint", reasons)

    def test_resume_with_hash_drift_fails_before_model(self):
        sample = self.root / "sample.txt"
        sample.write_text("alpha\n")
        checkpoint = agent.build_run_checkpoint(
            mode="general", task="continue", phase="tool_completed",
            tracked_paths=["sample.txt"],
        )
        agent.save_run_checkpoint(checkpoint)
        sample.write_text("changed\n")
        env = {**__import__("os").environ, "LAI_DATA_DIR": str(self.base / "data")}
        result = subprocess.run(
            [str(SOURCE), "--resume"], cwd=self.root, env=env,
            text=True, capture_output=True, timeout=5, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Recovery blocked", result.stderr)
        self.assertIn("tracked file hash changed", result.stderr)

    def test_recovery_compatibility_fails_closed_when_git_evidence_unavailable(self):
        checkpoint = agent.build_run_checkpoint(
            mode="general", task="continue", phase="started",
        )
        with mock.patch.object(agent, "workspace_git_branch", return_value="[unavailable]"):
            compatible, reasons = agent.check_recovery_compatibility(checkpoint)
        self.assertFalse(compatible)
        self.assertIn("Git branch evidence unavailable", reasons)

        with mock.patch.object(agent, "workspace_git_status", return_value="[unavailable]"):
            compatible, reasons = agent.check_recovery_compatibility(checkpoint)
        self.assertFalse(compatible)
        self.assertIn("Git status evidence unavailable", reasons)

    def test_recovery_status_blocks_malformed_hash_map(self):
        checkpoint = agent.build_run_checkpoint(
            mode="general", task="continue", phase="started",
        )
        checkpoint["tracked_hashes"] = ["not-a-map"]
        agent.save_run_checkpoint(checkpoint)
        state = agent.inspect_recovery_checkpoint()
        self.assertEqual(state["status"], "blocked")
        self.assertFalse(state["resumable"])
        self.assertIn("tracked hash map is invalid", state["reasons"])

    def test_terminal_checkpoint_is_not_resumable(self):
        checkpoint = agent.build_run_checkpoint(
            mode="general", task="done", phase="completed", terminal=True,
        )
        agent.save_run_checkpoint(checkpoint)
        status = agent.inspect_recovery_checkpoint()
        self.assertEqual(status["status"], "terminal")
        self.assertFalse(status["resumable"])

    def test_deterministic_recovery_status_needs_no_server(self):
        checkpoint = agent.build_run_checkpoint(
            mode="general", task="continue", phase="started",
        )
        agent.save_run_checkpoint(checkpoint)
        env = {**__import__("os").environ, "LAI_DATA_DIR": str(self.base / "data")}
        result = subprocess.run(
            [str(SOURCE), "--recovery"], cwd=self.root, env=env,
            text=True, capture_output=True, check=True,
        )
        self.assertIn("# lai recovery", result.stdout)
        self.assertIn("Status: interrupted", result.stdout)

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

    def test_recovery_clear_removes_checkpoint_snapshot_without_model(self):
        sample = self.root / "sample.txt"
        sample.write_text("private rollback content\n", encoding="utf-8")
        checkpoint = agent.build_run_checkpoint("plan", "synthetic task", "started", tracked_paths=["sample.txt"])
        agent.save_run_checkpoint(checkpoint)
        agent.capture_prewrite_snapshots(checkpoint["run_id"], ["sample.txt"])
        self.assertTrue(agent.run_checkpoint_path().is_file())
        self.assertTrue(agent.run_snapshot_path(checkpoint["run_id"]).is_file())
        buffer = io.StringIO()
        with mock.patch.object(agent, "CLI_ARGS", ["--recovery", "clear"]), \
                mock.patch.object(agent, "api_call") as api_call, \
                redirect_stdout(buffer):
            agent.main()
        self.assertIn("Recovery checkpoint cleared.", buffer.getvalue())
        self.assertIn("Recovery snapshot cleared.", buffer.getvalue())
        self.assertNotIn("private rollback content", buffer.getvalue())
        self.assertFalse(agent.run_checkpoint_path().exists())
        self.assertFalse(agent.run_snapshot_path(checkpoint["run_id"]).exists())
        api_call.assert_not_called()

        buffer = io.StringIO()
        with mock.patch.object(agent, "CLI_ARGS", ["--recovery", "--help"]), \
                redirect_stdout(buffer):
            agent.main()
        self.assertIn("Usage: lai recovery [clear]", buffer.getvalue())

    def test_checkpoint_cli_lists_and_shows_active_checkpoint_without_model(self):
        sample = self.root / "sample.txt"
        sample.write_text("stable\n", encoding="utf-8")
        checkpoint = agent.build_run_checkpoint(
            "implement", "synthetic task", "tool_completed",
            tracked_paths=["sample.txt"], last_tool="edit",
        )
        agent.save_run_checkpoint(checkpoint)

        list_payload = json.loads(agent.render_checkpoint_list(json_mode=True))
        self.assertEqual(list_payload["checkpoint_count"], 1)
        listed = list_payload["checkpoints"][0]
        self.assertEqual(listed["run_id"], checkpoint["run_id"])
        self.assertEqual(listed["mode"], "implement")
        self.assertEqual(listed["tracked_path_count"], 1)
        self.assertEqual(listed["tracked_paths"], ["sample.txt"])
        self.assertTrue(listed["resumable"])

        shown = json.loads(agent.render_checkpoint_show(checkpoint["run_id"], json_mode=True))
        self.assertEqual(shown["checkpoint"]["run_id"], checkpoint["run_id"])
        self.assertEqual(shown["checkpoint"]["last_tool"], "edit")

        shown_last = json.loads(agent.render_checkpoint_show("--last", json_mode=True))
        self.assertEqual(shown_last["checkpoint"]["run_id"], checkpoint["run_id"])

        with self.assertRaises(SystemExit):
            agent.render_checkpoint_show("missing-run", json_mode=True)

        buffer = io.StringIO()
        with mock.patch.object(agent, "CLI_ARGS", ["--checkpoint", "list", "--json"]), \
                mock.patch.object(agent, "api_call") as api_call, \
                redirect_stdout(buffer):
            agent.main()
        self.assertEqual(json.loads(buffer.getvalue())["checkpoint_count"], 1)
        api_call.assert_not_called()

    def test_prewrite_snapshot_captures_private_content_and_public_metadata(self):
        sample = self.root / "sample.txt"
        sample.write_text("before secret-ish text\n", encoding="utf-8")
        payload = agent.capture_prewrite_snapshots(
            "run-123", ["sample.txt", "created.txt", "sample.txt"]
        )
        self.assertEqual(payload["run_id"], "run-123")
        self.assertEqual(len(payload["files"]), 2)
        by_path = {item["path"]: item for item in payload["files"]}
        self.assertTrue(by_path["sample.txt"]["exists"])
        self.assertEqual(by_path["sample.txt"]["content"], "before secret-ish text\n")
        self.assertFalse(by_path["created.txt"]["exists"])
        self.assertTrue(agent.run_snapshot_path("run-123").is_file())
        self.assertNotIn(self.root.name, str(agent.run_snapshot_path("run-123").parent))

        sample.write_text("after\n", encoding="utf-8")
        second = agent.capture_prewrite_snapshots("run-123", ["sample.txt"])
        by_path = {item["path"]: item for item in second["files"]}
        self.assertEqual(by_path["sample.txt"]["content"], "before secret-ish text\n")

        public = json.loads(agent.render_snapshot_show("run-123", json_mode=True))
        rendered = json.dumps(public)
        self.assertEqual(public["snapshot"]["file_count"], 2)
        self.assertNotIn("before secret-ish text", rendered)
        self.assertIn("content_bytes", rendered)
        self.assertIn("sample.txt", rendered)

        buffer = io.StringIO()
        with mock.patch.object(agent, "CLI_ARGS", ["--snapshot", "show", "run-123", "--json"]), \
                mock.patch.object(agent, "api_call") as api_call, \
                redirect_stdout(buffer):
            agent.main()
        self.assertEqual(json.loads(buffer.getvalue())["snapshot"]["file_count"], 2)
        api_call.assert_not_called()

    def test_rollback_restores_snapshot_only_when_checkpoint_hash_matches(self):
        sample = self.root / "sample.txt"
        created = self.root / "created.txt"
        sample.write_text("before\n", encoding="utf-8")
        agent.capture_prewrite_snapshots("run-rollback", ["sample.txt", "created.txt"])
        sample.write_text("after\n", encoding="utf-8")
        sample.chmod(0o600)
        created.write_text("new file\n", encoding="utf-8")
        checkpoint = agent.build_run_checkpoint(
            "implement", "rollback task", "tool_completed",
            tracked_paths=["sample.txt", "created.txt"],
        )
        checkpoint["run_id"] = "run-rollback"
        agent.save_run_checkpoint(checkpoint)

        dry_run = json.loads(agent.render_rollback(["run-rollback", "--dry-run", "--json"]))
        self.assertEqual(dry_run["action_count"], 2)
        self.assertEqual(dry_run["blocked_count"], 0)
        self.assertTrue(sample.is_file())
        self.assertTrue(created.is_file())

        applied = json.loads(agent.render_rollback(["run-rollback", "--json"]))
        self.assertEqual(applied["action_count"], 2)
        self.assertEqual(applied["blocked_count"], 0)
        self.assertEqual(sample.read_text(encoding="utf-8"), "before\n")
        self.assertEqual(sample.stat().st_mode & 0o777, 0o600)
        self.assertFalse(created.exists())

        sample.write_text("external drift\n", encoding="utf-8")
        blocked = agent.collect_rollback_plan("run-rollback", dry_run=True)
        self.assertEqual(blocked["action_count"], 0)
        self.assertGreaterEqual(blocked["blocked_count"], 1)
        self.assertIn("current file hash differs", json.dumps(blocked))

        buffer = io.StringIO()
        with mock.patch.object(agent, "CLI_ARGS", ["--rollback", "--last", "--dry-run", "--json"]), \
                mock.patch.object(agent, "api_call") as api_call, \
                redirect_stdout(buffer):
            agent.main()
        self.assertIn("blocked_count", buffer.getvalue())
        api_call.assert_not_called()

    def test_configuration_helpers_are_reexported_from_typed_module(self):
        import lai_config

        self.assertIs(agent.load_configuration, lai_config.load_configuration)
        self.assertIs(agent.path_status, lai_config.path_status)
        self.assertEqual(agent.DEFAULT_MODEL, lai_config.DEFAULT_MODEL)

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

    def test_configuration_rejects_unknown_toml_keys(self):
        config_file = self.root / "config.toml"
        config_file.write_text("[lai]\nextra = 'bad'\n")
        with self.assertRaisesRegex(SystemExit, "unknown key"):
            agent.load_configuration(["--config", str(config_file)], environ={}, home=self.root)

    def test_configuration_rejects_invalid_types_and_empty_values(self):
        cases = [
            ("[lai]\nport = true\n", "port"),
            ("[lai]\nmodel = 42\n", "model"),
            ("[lai]\nserver_launcher = ''\n", "server_launcher"),
            ("[lai]\ndata_dir = 42\n", "data_dir"),
            ("[lai]\nhost = 'http://127.0.0.1:8080'\n", "host"),
        ]
        for index, (content, pattern) in enumerate(cases):
            with self.subTest(index=index):
                config_file = self.root / f"bad-{index}.toml"
                config_file.write_text(content)
                with self.assertRaisesRegex(SystemExit, pattern):
                    agent.load_configuration(["--config", str(config_file)], environ={}, home=self.root)

    def test_configuration_rejects_config_file_self_reference_in_toml(self):
        config_file = self.root / "config.toml"
        config_file.write_text("[lai]\nconfig_file = 'other.toml'\n")
        with self.assertRaisesRegex(SystemExit, "unknown key"):
            agent.load_configuration(["--config", str(config_file)], environ={}, home=self.root)

    def test_config_status_is_safe_and_deterministic(self):
        key_file = self.root / "secret-key"
        key_file.write_text("super-secret-test-key\n")
        values, _ = agent.load_configuration(
            ["--api-key-file", str(key_file), "--data-dir", str(self.base / "data")],
            environ={}, home=self.root,
        )
        shown = agent.render_config_status(values)
        self.assertIn("# lai config", shown)
        self.assertIn("api_key_file", shown)
        self.assertIn("Checks:", shown)
        self.assertIn("OK", shown)
        self.assertNotIn("super-secret-test-key", shown)

    def test_deterministic_config_cli_needs_no_server(self):
        key_file = self.root / "secret-key"
        key_file.write_text("super-secret-test-key\n")
        env = {
            **__import__("os").environ,
            "LAI_API_KEY_FILE": str(key_file),
            "LAI_DATA_DIR": str(self.base / "data"),
        }
        result = subprocess.run(
            [str(SOURCE.parent / "lai"), "config"],
            cwd=self.root, env=env, text=True, capture_output=True,
            timeout=5, check=True,
        )
        self.assertIn("# lai config", result.stdout)
        self.assertIn("api_key_file", result.stdout)
        self.assertNotIn("super-secret-test-key", result.stdout)

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

    def test_spec_helpers_use_typed_module_with_root_aware_wrappers(self):
        import lai_specs

        self.assertIs(agent.parse_spec, lai_specs.parse_spec)
        self.assertIs(agent.markdown_section, lai_specs.markdown_section)
        self.assertIsNot(agent.load_active_spec, lai_specs.load_active_spec)
        self.assertIsNot(agent.render_active_spec_context, lai_specs.render_active_spec_context)

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

    def test_main_injects_ranked_context_only_in_selected_modes(self):
        candidate = [{
            "path": "src/worker.py", "score": 80,
            "reasons": ["task_path_match", "git_changed"],
        }]
        selected = ["--plan", "--debug", "--fix", "--implement", "--refactor"]
        for flag in selected:
            captured = {}

            def stop_at_model(host, messages, **kwargs):
                captured["messages"] = messages
                raise RuntimeError("STOP_AT_MODEL")

            with self.subTest(flag=flag), \
                 mock.patch.object(agent, "CLI_ARGS", [flag, "repair worker"]), \
                 mock.patch.object(agent, "server_ready", return_value=True), \
                 mock.patch.object(agent, "rank_context_candidates", return_value=candidate), \
                 mock.patch.object(agent, "load_mode_skill", return_value="synthetic skill"), \
                 mock.patch.object(agent, "api_call", side_effect=stop_at_model), \
                 mock.patch.object(agent, "record_metric_event"), \
                 mock.patch.object(agent, "record_audit_event"):
                with self.assertRaisesRegex(RuntimeError, "STOP_AT_MODEL"):
                    agent.main()

            system = captured["messages"][0]["content"]
            self.assertIn("CONTEXT MAP", system)
            self.assertIn("metadata_only_not_evidence", system)
            self.assertIn("CONTEXT CANDIDATES", system)
            self.assertIn("src/worker.py", system)

        captured = {}

        def stop_general(host, messages, **kwargs):
            captured["messages"] = messages
            raise RuntimeError("STOP_AT_MODEL")

        with mock.patch.object(agent, "CLI_ARGS", ["plain task"]), \
             mock.patch.object(agent, "server_ready", return_value=True), \
             mock.patch.object(agent, "rank_context_candidates", return_value=candidate), \
             mock.patch.object(agent, "api_call", side_effect=stop_general), \
             mock.patch.object(agent, "record_metric_event"), \
             mock.patch.object(agent, "record_audit_event"):
            with self.assertRaisesRegex(RuntimeError, "STOP_AT_MODEL"):
                agent.main()

        system = captured["messages"][0]["content"]
        self.assertNotIn("CONTEXT MAP", system)
        self.assertNotIn("CONTEXT CANDIDATES", system)

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

        self.assertIn("# lai active spec", result.stdout)
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
        self.assertEqual(result.stdout.strip(), f"lai harness {agent.VERSION}")

    def test_deterministic_model_eval_plan_needs_no_server(self):
        result = subprocess.run(
            [str(SOURCE), "--model-eval", "plan"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("# lai model evaluation", result.stdout)
        self.assertIn("Current model:", result.stdout)
        self.assertIn("implement-small-diff", result.stdout)
        self.assertIn("does not call, start, or download a model", result.stdout)

    def test_gateway_contract_cli_is_deterministic_and_secret_free(self):
        env = {**os.environ, "LAI_DATA_DIR": str(self.base / "data")}
        result = subprocess.run(
            [str(SOURCE), "--gateway-contract", "--json"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["product"], agent.PRODUCT_NAME)
        self.assertEqual(payload["version"], agent.VERSION)
        self.assertEqual(payload["companion"]["name"], "lai-gateway")
        self.assertFalse(payload["capabilities"]["shell_execution"])
        self.assertFalse(payload["capabilities"]["direct_llama_proxy"])
        self.assertIn("control_token_or_model_api_key_disclosure", payload["forbidden_capabilities"])
        self.assertIn("/v1/gateway-contract", [route["path"] for route in payload["routes"]])
        self.assertNotIn("synthetic-test-key", result.stdout)
        self.assertNotIn("llama-api-key", result.stdout)

        wrapped = subprocess.run(
            [str(SOURCE.parent / "lai"), "gateway-contract", "--json"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=5,
            check=True,
        )
        self.assertEqual(json.loads(wrapped.stdout), payload)


    def test_deterministic_semantics_cli_needs_no_server(self):
        result = subprocess.run(
            [str(SOURCE), "--semantics"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("# lai code semantics", result.stdout)
        self.assertIn("policy-gateway", result.stdout)
        self.assertIn("src/local-agent", result.stdout)
        self.assertIn("advisory metadata", result.stdout)

        raw = subprocess.run(
            [str(SOURCE), "--semantics", "--json"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(raw.stdout)
        self.assertEqual(payload["product"], "lai harness")
        subsystem_ids = {item["id"] for item in payload["contract"]["subsystems"]}
        self.assertIn("context-intelligence", subsystem_ids)
        self.assertIn("policy-gateway", subsystem_ids)
        self.assertIn("semantic-code-contracts", subsystem_ids)
        semantic = next(
            item for item in payload["contract"]["subsystems"]
            if item["id"] == "semantic-code-contracts"
        )
        self.assertIn("src/lai_semantics.py", semantic["paths"])
        configuration = next(
            item for item in payload["contract"]["subsystems"]
            if item["id"] == "configuration"
        )
        self.assertEqual(configuration["paths"][0], "src/lai_config.py")
        spec_workflow = next(
            item for item in payload["contract"]["subsystems"]
            if item["id"] == "spec-workflow"
        )
        self.assertEqual(spec_workflow["paths"][0], "src/lai_specs.py")
        remote_sessions = next(
            item for item in payload["contract"]["subsystems"]
            if item["id"] == "remote-sessions"
        )
        self.assertEqual(remote_sessions["paths"][0], "src/lai_sessions.py")
        web_evidence = next(
            item for item in payload["contract"]["subsystems"]
            if item["id"] == "web-evidence"
        )
        self.assertEqual(web_evidence["paths"][0], "src/lai_web.py")

    def test_deterministic_model_eval_json_and_sample_are_parseable(self):
        result = subprocess.run(
            [str(SOURCE), "--model-eval", "plan", "--json"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["product"], "lai harness")
        self.assertEqual(payload["version"], agent.VERSION)
        scenario_ids = {item["id"] for item in payload["scenarios"]}
        self.assertIn("context-ranking", scenario_ids)

        sample = subprocess.run(
            [str(SOURCE), "--model-eval", "sample"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )
        records = [json.loads(line) for line in sample.stdout.splitlines()]
        self.assertEqual(len(records), len(agent.MODEL_EVALUATION_SCENARIOS))
        self.assertEqual(records[0]["outcome"], "not_run")
        self.assertEqual(records[0]["validation"], "not_run")
        normalized = agent.normalize_model_eval_record(records[0], 1)
        self.assertEqual(agent.score_model_evaluation_record(normalized), 0.0)

    def test_model_eval_scoring_ranks_models(self):
        results_dir = self.root / "model-eval"
        results_dir.mkdir()
        records = [
            {
                "model": "ministral-baseline",
                "scenario": "implement-small-diff",
                "outcome": "pass",
                "validation": "pass",
                "latency_ms": 80000,
                "tool_calls": 6,
                "truncation_retries": 0,
                "policy_blocks": 0,
                "hallucination_flags": 0,
            },
            {
                "model": "qwen-candidate",
                "scenario": "implement-small-diff",
                "outcome": "partial",
                "validation": "fail",
                "latency_ms": 180000,
                "tool_calls": 11,
                "truncation_retries": 1,
                "policy_blocks": 1,
                "hallucination_flags": 1,
            },
        ]
        path = results_dir / "results.jsonl"
        path.write_text("\n".join(json.dumps(item) for item in records) + "\n")

        result = subprocess.run(
            [str(SOURCE), "--model-eval", "score", "model-eval/results.jsonl"],
            cwd=self.root,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("# lai model evaluation score", result.stdout)
        self.assertLess(
            result.stdout.index("## ministral-baseline"),
            result.stdout.index("## qwen-candidate"),
        )
        self.assertIn("average_score: 100.0", result.stdout)

    def test_model_eval_score_resolves_saved_result_basename(self):
        data_dir = self.base / "data"
        result_dir = data_dir / "model-eval"
        result_dir.mkdir(parents=True)
        record = {
            "model": "saved-model",
            "scenario": "plan-repo-change",
            "outcome": "pass",
            "validation": "pass",
            "latency_ms": 10,
            "prompt_tokens": 1,
            "completion_tokens": 1,
            "tool_calls": 1,
            "truncation_retries": 0,
            "policy_blocks": 0,
            "hallucination_flags": 0,
        }
        (result_dir / "saved.jsonl").write_text(json.dumps(record) + "\n")

        result = subprocess.run(
            [str(SOURCE), "--model-eval", "score", "saved.jsonl"],
            cwd=self.root,
            env={**os.environ, "LAI_DATA_DIR": str(data_dir)},
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("## saved-model", result.stdout)
        self.assertIn("average_score: 100.0", result.stdout)

    def test_model_eval_score_rejects_bad_paths_and_records(self):
        outside = self.base / "outside.jsonl"
        outside.write_text("{}\n")
        escaped = subprocess.run(
            [str(SOURCE), "--model-eval", "score", "../outside.jsonl"],
            cwd=self.root,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(escaped.returncode, 0)
        self.assertIn("outside repository", escaped.stderr.lower())

        bad_path = self.root / "bad.jsonl"
        bad_path.write_text(json.dumps({
            "model": "bad",
            "scenario": "plan-repo-change",
            "outcome": "pass",
            "validation": "pass",
            "latency_ms": -1,
        }) + "\n")
        bad = subprocess.run(
            [str(SOURCE), "--model-eval", "score", "bad.jsonl"],
            cwd=self.root,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("latency_ms must be a non-negative number", bad.stderr)

    def test_model_eval_runner_fixtures_are_versioned_and_model_backed(self):
        payload = agent.load_model_evaluation_fixtures()
        self.assertEqual(payload["schema_version"], 1)
        fixture_ids = {item["id"] for item in payload["fixtures"]}
        self.assertEqual(fixture_ids, agent.MODEL_EVALUATION_MODEL_BACKED_SCENARIOS)
        for fixture in payload["fixtures"]:
            self.assertIn(fixture["mode"], {"plan", "debug", "implement", "review", "security"})
            self.assertTrue(fixture["prompt"])
            self.assertIsInstance(fixture["expected"]["required_output_patterns"], list)
            self.assertIn(fixture["expected"]["validation_profile"], {None, "python-unittest"})
            self.assertNotIn("validation_command", fixture["expected"])

    def test_model_eval_validation_profiles_are_allowlisted(self):
        self.assertIsNone(agent.model_evaluation_validation_argv(None))
        argv = agent.model_evaluation_validation_argv("python-unittest")
        self.assertEqual(argv, [agent.sys.executable, "-m", "unittest", "test_math_utils.py"])
        with self.assertRaises(ValueError):
            agent.model_evaluation_validation_argv("arbitrary-command")

    def test_model_eval_claim_flags_detect_false_claims_and_impossible_lines(self):
        fixture = next(
            item for item in agent.load_model_evaluation_fixtures()["fixtures"]
            if item["id"] == "implement-small-diff"
        )
        output = "Implemented the fix. Validation: tests passed. Evidence: line 42."
        flags = agent.model_evaluation_claim_flags(
            output, "", "", 1, fixture
        )
        self.assertIn("claimed_edit_without_diff", flags)
        self.assertIn("claimed_validation_success_but_validator_failed", flags)
        self.assertIn("impossible_line_reference", flags)

    def test_model_eval_validation_fails_false_implementation_claim(self):
        fixture = next(
            item for item in agent.load_model_evaluation_fixtures()["fixtures"]
            if item["id"] == "implement-small-diff"
        )
        proc = subprocess.CompletedProcess(
            ["agent"], 0, stdout="Implemented math_utils.py; tests passed.", stderr=""
        )
        validator = subprocess.CompletedProcess(["python3"], 1, stdout="FAILED", stderr="")
        result = agent.model_evaluation_validate_result(
            fixture, proc, "", [], "", [], validator
        )
        self.assertEqual(result["outcome"], "fail")
        self.assertEqual(result["validation"], "fail")
        self.assertGreaterEqual(result["hallucination_flags"], 2)

    def test_model_eval_run_args_repeat_is_bounded(self):
        options = agent.parse_model_evaluation_run_args([
            "--scenario", "plan-repo-change", "--repeat", "2", "--json"
        ])
        self.assertEqual(options["scenarios"], ["plan-repo-change"])
        self.assertEqual(options["repeat"], 2)
        self.assertTrue(options["json"])
        for bad in ("0", "6", "nope"):
            with self.assertRaises(SystemExit):
                agent.parse_model_evaluation_run_args(["--repeat", bad])

    def test_model_eval_run_persists_versioned_results_outside_repository(self):
        old_data = agent.DATA_BASE
        agent.DATA_BASE = self.base / "data"
        record = {
            "model": "synthetic-model",
            "scenario": "plan-repo-change",
            "outcome": "pass",
            "validation": "pass",
            "latency_ms": 10,
            "prompt_tokens": 5,
            "completion_tokens": 2,
            "tool_calls": 1,
            "truncation_retries": 0,
            "policy_blocks": 0,
            "hallucination_flags": 0,
            "notes": "",
            "agent_exit_code": 0,
            "changed_paths": [],
            "response_sha256": "0" * 64,
            "response_excerpt": "ok",
        }
        profile = {
            "host": "127.0.0.1", "port": 8080, "model_alias": "synthetic-model",
            "model_ftype": "Q4_K_M", "context_size": 16384, "total_slots": 1,
        }
        try:
            with mock.patch.object(agent, "model_evaluation_server_profile", return_value=profile), \
                    mock.patch.object(agent, "model_evaluation_source_state", return_value={"head": "abc123", "status": ""}), \
                    mock.patch.object(agent, "run_model_evaluation_fixture", side_effect=lambda *a, **k: dict(record)):
                summary, records, json_mode = agent.run_model_evaluation([
                    "--scenario", "plan-repo-change", "--repeat", "2"
                ])
        finally:
            agent.DATA_BASE = old_data
        self.assertFalse(json_mode)
        self.assertEqual(len(records), 2)
        self.assertFalse(summary["decision_eligible"])
        self.assertEqual(summary["repeat"], 2)
        results_path = Path(summary["results_path"])
        summary_path = Path(summary["summary_path"])
        self.assertTrue(results_path.is_file())
        self.assertTrue(summary_path.is_file())
        self.assertFalse(results_path.resolve().is_relative_to(self.root.resolve()))
        persisted = [json.loads(line) for line in results_path.read_text().splitlines()]
        self.assertEqual([item["sample_index"] for item in persisted], [1, 2])

    def test_model_eval_score_accepts_multiple_lai_data_files(self):
        data_dir = self.base / "score-data"
        results_dir = data_dir / "model-eval"
        results_dir.mkdir(parents=True)
        base = {
            "scenario": "plan-repo-change", "outcome": "pass", "validation": "pass",
            "latency_ms": 100, "tool_calls": 1, "truncation_retries": 0,
            "policy_blocks": 0, "hallucination_flags": 0,
        }
        first = results_dir / "one.jsonl"
        second = results_dir / "two.jsonl"
        first.write_text(json.dumps({**base, "model": "model-one"}) + "\n")
        second.write_text(json.dumps({**base, "model": "model-two"}) + "\n")
        env = {**os.environ, "LAI_DATA_DIR": str(data_dir)}
        result = subprocess.run(
            [str(SOURCE), "--model-eval", "score", str(first), str(second)],
            cwd=self.root, env=env, text=True, capture_output=True, check=True,
        )
        self.assertIn("## model-one", result.stdout)
        self.assertIn("## model-two", result.stdout)
        self.assertIn("decision_eligible: no", result.stdout)

    def test_branding_doc_preserves_lai_command_and_compatibility_ids(self):
        branding = (Path(__file__).parents[1] / "docs" / "BRANDING.md").read_text()
        self.assertIn("lai harness", branding)
        self.assertIn("lai", branding)
        self.assertIn("local-agent", branding)
        self.assertIn("lai-local-agent", branding)
        self.assertIn("lai-chat", branding)

    def test_public_repository_urls_use_lai_harness_slug(self):
        repo = Path(__file__).parents[1]
        expected = "https://github.com/fenatodev/lai-harness.git"
        for rel in ("README.md", "README.pt-BR.md", "vscode-extension/package.json"):
            text = (repo / rel).read_text(encoding="utf-8")
            self.assertIn(expected, text)
            self.assertNotIn("https://github.com/fenatodev/lai-local-agent.git", text)

    def test_public_publishing_surface_is_channel_aware_and_current_release_is_documented(self):
        repo = Path(__file__).parents[1]
        publishing = (repo / "docs" / "GITHUB-PUBLISHING.md").read_text(encoding="utf-8")
        release_notes = (repo / "docs" / "RELEASE-NOTES.md").read_text(encoding="utf-8")
        release_checklist = (repo / "docs" / "RELEASE-CHECKLIST.md").read_text(encoding="utf-8")
        release_pack = (repo / "docs" / "RELEASE-PACK.md").read_text(encoding="utf-8")
        stable_readiness = (repo / "docs" / "STABLE-READINESS.md").read_text(encoding="utf-8")
        package_script = (repo / "scripts" / "package-vsix.sh").read_text(encoding="utf-8")
        validate_script = (repo / "scripts" / "validate.sh").read_text(encoding="utf-8")

        self.assertIn("**Name:** `lai-harness`", publishing)
        self.assertIn("release channel (`prerelease` or `stable`)", publishing)
        self.assertIn("expected GitHub `prerelease` flag", publishing)
        self.assertTrue(
            release_notes.startswith(f"## lai harness v{agent.VERSION} — ")
        )
        self.assertIn("lai harness v0.4.0 — stable core graduation", release_notes)
        self.assertIn("lai harness v0.4.0-beta.24", release_notes)
        self.assertIn("<target-version>", release_checklist)
        self.assertIn("pre-release flag", release_checklist)
        self.assertIn("release_channel=stable", release_pack)
        self.assertIn("expected_prerelease=false", release_pack)
        self.assertIn("Explicitly deferred from the v0.4.0 gate", stable_readiness)
        self.assertIn("not blockers", stable_readiness)
        self.assertNotIn("Release v0.3.0", publishing)
        self.assertNotIn("**Name:** `lai-local-agent`", publishing)
        self.assertIn("/tmp/lai-harness-${version}.vsix", package_script)
        self.assertIn("/tmp/lai-harness-validation.vsix", validate_script)

    def test_public_docs_do_not_use_old_product_title(self):
        repo = Path(__file__).parents[1]
        allowed = {
            repo / "docs" / "BRANDING.md",
            repo / ".specs" / "006-lai-harness-branding.md",
        }
        public_roots = [repo / "README.md", repo / "README.pt-BR.md", repo / "docs", repo / "vscode-extension"]
        stale = []
        for root in public_roots:
            paths = [root] if root.is_file() else root.rglob("*.md")
            for candidate in paths:
                if candidate in allowed:
                    continue
                text = candidate.read_text(encoding="utf-8")
                if (
                    "LAI Harness" in text
                    or "LAI — Local AI Agent" in text
                    or "# LAI —" in text
                ):
                    stale.append(candidate.relative_to(repo).as_posix())
        self.assertEqual(stale, [])

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

    def test_context_task_terms_normalize_accents(self):
        terms = agent.context_task_terms("corrigir autenticação do usuário")
        self.assertIn("autenticacao", terms)
        self.assertIn("usuario", terms)

    def test_context_inventory_is_bounded_and_excludes_generated_and_symlinks(self):
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text("print('ok')\n")
        (self.root / ".github" / "workflows").mkdir(parents=True)
        (self.root / ".github" / "workflows" / "ci.yml").write_text("name: CI\n")
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules" / "noise.js").write_text("noise\n")
        (self.root / "link.py").symlink_to(self.root / "src" / "app.py")
        files = agent.repository_context_inventory(max_files=20)
        self.assertIn("src/app.py", files)
        self.assertIn(".github/workflows/ci.yml", files)
        self.assertNotIn("node_modules/noise.js", files)
        self.assertNotIn("link.py", files)
        self.assertLessEqual(len(files), 20)

    def test_context_ranking_combines_explainable_signals(self):
        (self.root / "src").mkdir()
        (self.root / "src" / "worker.py").write_text("timeout = 30\n")
        (self.root / "src" / "noise.py").write_text("unrelated = True\n")
        state = {"recent_files": ["src/worker.py"], "modified_files": []}
        spec = {"text": "Change `src/worker.py` timeout behavior."}
        with mock.patch.object(agent, "context_git_changed_paths", return_value={"src/worker.py"}):
            ranked = agent.rank_context_candidates(
                "repair worker timeout", workspace_state=state, active_spec=spec, limit=8,
            )
        self.assertEqual(ranked[0]["path"], "src/worker.py")
        reasons = set(ranked[0]["reasons"])
        self.assertIn("git_changed", reasons)
        self.assertIn("recent", reasons)
        self.assertIn("spec_reference", reasons)
        self.assertIn("task_path_match", reasons)
        self.assertIn("content_match", reasons)

    def test_context_ranking_uses_semantic_contracts(self):
        (self.root / "src").mkdir()
        (self.root / "docs").mkdir()
        (self.root / ".agents" / "rules").mkdir(parents=True)
        (self.root / "src" / "local-agent").write_text("policy runtime\n")
        (self.root / "docs" / "SECURITY-MODEL.md").write_text("safety model\n")
        (self.root / ".agents" / "rules" / "core-safety.md").write_text("approval rules\n")

        with mock.patch.object(agent, "context_git_changed_paths", return_value=set()):
            ranked = agent.rank_context_candidates(
                "melhorar policy approval safety",
                workspace_state={},
                active_spec=None,
                limit=8,
            )

        by_path = {item["path"]: item for item in ranked}
        self.assertIn("src/local-agent", by_path)
        self.assertIn(
            "semantic_contract:policy-gateway",
            by_path["src/local-agent"]["reasons"],
        )
        self.assertIn("docs/SECURITY-MODEL.md", by_path)

    def test_context_ranking_is_deterministic(self):
        (self.root / "a.py").write_text("target token\n")
        (self.root / "b.py").write_text("target token\n")
        with mock.patch.object(agent, "context_git_changed_paths", return_value=set()):
            first = agent.rank_context_candidates("target token", workspace_state={}, limit=8)
            second = agent.rank_context_candidates("target token", workspace_state={}, limit=8)
        self.assertEqual(first, second)
        self.assertEqual([item["path"] for item in first], sorted(item["path"] for item in first))

    def test_context_render_is_metadata_only_and_bounded(self):
        candidates = [{
            "path": "src/worker.py", "score": 99,
            "reasons": ["git_changed", "content_match"],
        }]
        shown = agent.render_context_candidates(candidates, max_chars=180)
        self.assertIn("src/worker.py", shown)
        self.assertIn("git_changed", shown)
        self.assertNotIn("timeout = 30", shown)
        self.assertLessEqual(len(shown), 180)
    def test_context_tool_exposes_metadata_views_without_shell_or_bodies(self):
        (self.root / "module.py").write_text("def worker():\n    return 'secret-body'\n")
        (self.root / "Makefile").write_text("test:\n\t@echo secret-body\n")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_context_tool.py").write_text(
            "def test_tool():\n    assert 'secret-body'\n"
        )
        changes = agent.tool_context({"operation": "changes", "limit": 5})
        checks = agent.tool_context({"operation": "checks", "limit": 5})
        tests_alias = agent.tool_context({"operation": "tests", "limit": 5})
        runs = agent.tool_context({"operation": "runs", "limit": 5})
        symbols = agent.tool_context({"operation": "symbols", "path": "module.py", "limit": 5})
        repo_map = agent.tool_context({"operation": "map", "max_files": 20, "max_paths": 4})
        self.assertIn("# lai context changes", changes)
        self.assertIn("# lai context checks", checks)
        self.assertIn("# lai context checks", tests_alias)
        self.assertIn("# lai context runs", runs)
        self.assertIn("# lai context symbols", symbols)
        self.assertIn("# lai context map", repo_map)
        self.assertIn("worker", symbols)
        combined = changes + checks + tests_alias + runs + symbols + repo_map
        self.assertNotIn("secret-body", combined)
        self.assertNotIn("```", combined)
        self.assertIn("metadata", combined.lower())
        self.assertEqual(
            agent.evaluate_tool_policy("context", {"operation": "map"}, mode="plan")["decision"],
            "ALLOW",
        )

    def test_context_runs_are_metadata_only_and_secret_free(self):
        run = agent.empty_run_history_record("run-123")
        run.update({
            "last_ts": "2026-09-07T00:00:00Z",
            "mode": "implement",
            "status": "completed",
            "tool_calls": 2,
            "tools": {"read": 1, "context": 1},
            "policy": {"ALLOW": 2},
            "validation_count": 1,
            "validation_events": [{
                "ts": "2026-09-07T00:00:01Z",
                "type": "validation",
                "command": "echo sk-secret-command",
                "result": "Traceback sk-secret-result",
            }],
            "events": [{
                "ts": "2026-09-07T00:00:01Z",
                "type": "validation",
                "command": "echo sk-secret-command",
                "result": "Traceback sk-secret-result",
            }],
            "modified_paths": ["src/local-agent"],
            "phases": ["started", "completed"],
        })
        recovery = {"status": "none", "resumable": False, "checkpoint": None, "reasons": []}
        with mock.patch.object(agent, "collect_run_history", return_value=[run]), \
             mock.patch.object(agent, "inspect_recovery_checkpoint", return_value=recovery):
            payload = agent.context_runs_payload(limit=5)
        dumped = json.dumps(payload)
        self.assertEqual(payload["runs_version"], 1)
        self.assertTrue(payload["metadata_only"])
        self.assertEqual(payload["repository"], ".")
        self.assertEqual(payload["runs"][0]["run_id"], "run-123")
        self.assertEqual(payload["runs"][0]["last_failure"]["status"], "fail")
        self.assertNotIn("command", payload["runs"][0]["last_failure"])
        self.assertNotIn("command", payload["runs"][0]["last_validation"])
        self.assertNotIn("sk-secret", dumped)
        rendered = agent.render_context_runs(payload)
        self.assertIn("# lai context runs", rendered)
        self.assertIn("run-123", rendered)
        self.assertNotIn("sk-secret", rendered)

    def test_deterministic_context_runs_cli_needs_no_server(self):
        env = {**os.environ, "LAI_DATA_DIR": str(self.base / "data")}
        result = subprocess.run(
            [str(SOURCE.parent / "lai"), "context", "runs", "--json", "--limit", "2"],
            cwd=self.root, env=env, text=True, capture_output=True,
            timeout=5, check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["runs_version"], 1)
        self.assertTrue(payload["metadata_only"])
        self.assertEqual(payload["repository"], ".")
        self.assertIn("checkpoint_status", payload)
        self.assertEqual(result.stderr, "")

    def test_context_checks_are_metadata_only_and_suggests_feedback(self):
        (self.root / "Makefile").write_text(
            "test:\n\t@echo sk-secret-test-body\ncheck:\n\t@echo ok\n",
            encoding="utf-8",
        )
        tests_dir = self.root / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_sample.py").write_text(
            "import unittest\n\n"
            "class SampleTest(unittest.TestCase):\n"
            "    def test_secret_body(self):\n"
            "        token = 'sk-secret-body'\n"
            "        self.assertTrue(token)\n",
            encoding="utf-8",
        )

        payload = agent.context_checks_payload(limit=5)
        dumped = json.dumps(payload)
        self.assertTrue(payload["metadata_only"])
        self.assertFalse(payload["inspected_content"])
        self.assertIn("test", payload["make_targets"])
        self.assertIn("check", payload["make_targets"])
        self.assertEqual(payload["test_files"][0]["path"], "tests/test_sample.py")
        self.assertEqual(payload["test_files"][0]["tests"], 1)
        self.assertIn("make test", [item["check"] for item in payload["suggested_feedback"]])
        self.assertNotIn("sk-secret", dumped)
        rendered = agent.render_context_checks(payload)
        self.assertIn("# lai context checks", rendered)
        self.assertIn("tests/test_sample.py", rendered)
        self.assertNotIn("sk-secret", rendered)

    def test_deterministic_context_checks_cli_needs_no_server(self):
        (self.root / "Makefile").write_text("test:\n\t@echo ok\n", encoding="utf-8")
        tests_dir = self.root / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_cli.py").write_text(
            "def test_cli_path():\n    assert True\n", encoding="utf-8"
        )
        env = {**os.environ, "LAI_DATA_DIR": str(self.base / "data")}
        result = subprocess.run(
            [str(SOURCE.parent / "lai"), "context", "checks", "--json", "--limit", "2"],
            cwd=self.root, env=env, text=True, capture_output=True,
            timeout=5, check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["checks_version"], 1)
        self.assertTrue(payload["metadata_only"])
        self.assertIn("test", payload["make_targets"])
        self.assertEqual(payload["test_files"][0]["path"], "tests/test_cli.py")

    def test_context_symbols_are_metadata_only_for_python_and_javascript(self):
        (self.root / "module.py").write_text(
            "SECRET = 'sk-not-real-secret'\n"
            "class Worker:\n"
            "    def run(self):\n"
            "        return SECRET\n"
            "def helper():\n"
            "    return SECRET\n",
            encoding="utf-8",
        )
        py_payload = agent.context_symbols_payload("module.py", limit=10)
        self.assertEqual(py_payload["parser"], "ok")
        self.assertTrue(py_payload["metadata_only"])
        names = {item["name"] for item in py_payload["symbols"]}
        self.assertIn("Worker", names)
        self.assertIn("Worker.run", names)
        self.assertIn("helper", names)
        self.assertNotIn("sk-not-real-secret", json.dumps(py_payload))

        (self.root / "app.js").write_text(
            "const token = 'sk-not-real-secret';\n"
            "class Ui {}\n"
            "function render() { return token; }\n"
            "const boot = () => token;\n",
            encoding="utf-8",
        )
        js_payload = agent.context_symbols_payload("app.js", limit=10)
        js_names = {item["name"] for item in js_payload["symbols"]}
        self.assertIn("Ui", js_names)
        self.assertIn("render", js_names)
        self.assertIn("boot", js_names)
        self.assertNotIn("sk-not-real-secret", json.dumps(js_payload))
        rendered = agent.render_context_symbols(py_payload)
        self.assertIn("# lai context symbols", rendered)
        self.assertNotIn("SECRET", rendered)

    def test_deterministic_context_symbols_cli_needs_no_server(self):
        (self.root / "module.py").write_text("def worker():\n    return 'secret-body'\n")
        env = {**__import__("os").environ, "LAI_DATA_DIR": str(self.base / "data")}
        result = subprocess.run(
            [str(SOURCE.parent / "lai"), "context", "symbols", "module.py", "--json", "--limit", "5"],
            cwd=self.root, env=env, text=True, capture_output=True,
            timeout=5, check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["symbols_version"], 1)
        self.assertTrue(payload["metadata_only"])
        self.assertEqual(payload["path"], "module.py")
        self.assertEqual(payload["symbols"][0]["name"], "worker")
        self.assertNotIn("secret-body", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_context_changes_are_metadata_only_bounded_and_secret_free(self):
        (self.root / "tracked.py").write_text("old value\n")
        subprocess.run(["git", "add", "tracked.py"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.root, check=True)
        (self.root / "tracked.py").write_text("new secret value\n")
        (self.root / "new.py").write_text("untracked secret value\n")
        payload = agent.context_git_changes_payload(limit=1)
        full_payload = agent.context_git_changes_payload(limit=10)
        self.assertEqual(payload["overall"], "dirty")
        self.assertTrue(payload["metadata_only"])
        self.assertEqual(payload["repository"], ".")
        self.assertEqual(payload["entry_limit"], 1)
        self.assertEqual(payload["entry_count"], 2)
        self.assertTrue(payload["entry_list_truncated"])
        self.assertEqual(payload["counts"]["unstaged"], 1)
        self.assertEqual(payload["counts"]["untracked"], 1)
        full_dumped = json.dumps(full_payload)
        self.assertIn("tracked.py", full_dumped)
        self.assertIn("new.py", full_dumped)
        dumped = json.dumps(payload) + full_dumped
        self.assertNotIn("new secret value", dumped)
        self.assertNotIn("untracked secret value", dumped)
        rendered = agent.render_context_changes(payload)
        self.assertIn("# lai context changes", rendered)
        self.assertIn("Metadata-only: true", rendered)
        self.assertNotIn("secret value", rendered)

    def test_deterministic_context_changes_cli_needs_no_server(self):
        (self.root / "worker.py").write_text("timeout = 30\n")
        env = {**__import__("os").environ, "LAI_DATA_DIR": str(self.base / "data")}
        result = subprocess.run(
            [str(SOURCE.parent / "lai"), "context", "changes", "--json", "--limit", "5"],
            cwd=self.root, env=env, text=True, capture_output=True,
            timeout=5, check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["changes_version"], 1)
        self.assertEqual(payload["overall"], "dirty")
        self.assertTrue(payload["metadata_only"])
        self.assertIn("worker.py", result.stdout)
        self.assertNotIn("timeout = 30", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_context_map_is_metadata_only_bounded_and_semantic(self):
        (self.root / "src").mkdir()
        (self.root / "docs").mkdir()
        (self.root / "src" / "local-agent").write_text("super secret implementation\n")
        (self.root / "docs" / "CONTEXT-INTELLIGENCE.md").write_text("context docs\n")
        (self.root / "README.md").write_text("readme\n")
        with mock.patch.object(agent, "context_git_changed_paths", return_value={"src/local-agent"}):
            payload = agent.repository_context_map(max_files=20, max_paths=2)
        self.assertTrue(payload["metadata_only"])
        self.assertFalse(payload["inspected_content"])
        self.assertEqual(payload["repository"], ".")
        self.assertEqual(payload["file_list_limit"], 2)
        self.assertLessEqual(len(payload["files"]), 2)
        self.assertIn("src/local-agent", payload["changed_paths"])
        self.assertNotIn("super secret implementation", json.dumps(payload))
        subsystems = {item["id"] for item in payload["semantic_subsystems"]}
        self.assertIn("context-intelligence", subsystems)
        rendered = agent.render_context_map(payload)
        self.assertIn("# lai context map", rendered)
        self.assertIn("Metadata-only: true", rendered)
        self.assertNotIn("super secret implementation", rendered)

    def test_deterministic_context_map_cli_needs_no_server(self):
        (self.root / "src").mkdir()
        (self.root / "src" / "worker.py").write_text("timeout = 30\n")
        env = {**__import__("os").environ, "LAI_DATA_DIR": str(self.base / "data")}
        result = subprocess.run(
            [str(SOURCE.parent / "lai"), "context", "map", "--json", "--max-files", "20", "--max-paths", "3"],
            cwd=self.root, env=env, text=True, capture_output=True,
            timeout=5, check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["map_version"], 1)
        self.assertTrue(payload["metadata_only"])
        self.assertFalse(payload["inspected_content"])
        self.assertLessEqual(len(payload["files"]), 3)
        self.assertNotIn("timeout = 30", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_deterministic_context_cli_needs_no_server(self):
        (self.root / "worker.py").write_text("timeout = 30\n")
        env = {**__import__("os").environ, "LAI_DATA_DIR": str(self.base / "data")}
        result = subprocess.run(
            [str(SOURCE.parent / "lai"), "context", "repair worker timeout"],
            cwd=self.root, env=env, text=True, capture_output=True,
            timeout=5, check=True,
        )
        self.assertIn("# lai context candidates", result.stdout)
        self.assertIn("worker.py", result.stdout)

    def test_context_ranking_degrades_when_git_signal_is_unavailable(self):
        (self.root / "worker.py").write_text("timeout = 30\n")
        with mock.patch.object(agent, "context_git_changed_paths", return_value=set()):
            ranked = agent.rank_context_candidates(
                "worker timeout", workspace_state={"recent_files": ["missing.py"]}, limit=8,
            )
        self.assertEqual(ranked[0]["path"], "worker.py")
        self.assertNotIn("missing.py", [item["path"] for item in ranked])


if __name__ == "__main__":
    unittest.main()
