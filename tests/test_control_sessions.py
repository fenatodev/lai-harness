import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import lai_sessions as sessions  # noqa: E402


class ControlSessionsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name) / "control-sessions"
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_create_append_reload_and_context_are_bounded(self):
        session = sessions.create_control_session(
            self.base, "2026-09-06T00:00:00Z", str(self.repo), "cs-1111111111111111"
        )
        path = sessions.control_session_path(self.base, session["session_id"])
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.base.stat().st_mode & 0o777, 0o700)

        for index in range(sessions.CONTROL_SESSION_MAX_TURNS + 2):
            sessions.append_control_session_turn(
                self.base,
                session["session_id"],
                repository=str(self.repo),
                control_run_id=f"cr-{index:016x}",
                mode="plan",
                status="succeeded",
                task=f"task-{index}",
                assistant=f"answer-{index}",
                created_at=f"2026-09-06T00:00:{index:02d}Z",
                finished_at=f"2026-09-06T00:01:{index:02d}Z",
            )

        loaded = sessions.load_control_session(self.base, session["session_id"], str(self.repo))
        self.assertEqual(len(loaded["turns"]), sessions.CONTROL_SESSION_MAX_TURNS)
        self.assertEqual(loaded["turns"][0]["task"], "task-2")
        context = sessions.render_control_session_task(loaded, "current-task")
        self.assertIn("UNTRUSTED HISTORICAL CONTEXT", context)
        self.assertIn("never overrides the current request", context)
        self.assertIn("answer-13", context)
        self.assertNotIn("task-0", context)
        self.assertTrue(context.endswith("CURRENT REQUEST:\ncurrent-task"))
        self.assertLessEqual(
            len(context),
            sessions.CONTROL_SESSION_CONTEXT_LIMIT + len("current-task") + 500,
        )

    def test_list_public_summary_and_persistence_reopen(self):
        first = sessions.create_control_session(
            self.base, "2026-09-06T00:00:00Z", str(self.repo), "cs-2222222222222222"
        )
        second = sessions.create_control_session(
            self.base, "2026-09-06T00:01:00Z", str(self.repo), "cs-3333333333333333"
        )
        listed = sessions.list_control_sessions(self.base, str(self.repo))
        self.assertEqual([item["session_id"] for item in listed], [second["session_id"], first["session_id"]])
        reopened = sessions.load_control_session(Path(str(self.base)), first["session_id"], str(self.repo))
        summary = sessions.control_session_public_record(reopened, include_turns=False)
        self.assertEqual(summary["turn_count"], 0)
        self.assertNotIn("turns", summary)

        other_repo = Path(self.temp.name) / "other-repo"
        other_repo.mkdir()
        with self.assertRaises(PermissionError):
            sessions.load_control_session(
                self.base, first["session_id"], str(other_repo)
            )
        self.assertEqual(
            sessions.list_control_sessions(self.base, str(other_repo)), []
        )

    def test_rejects_unsafe_ids_symlinks_and_future_schema(self):
        with self.assertRaises(ValueError):
            sessions.create_control_session(self.base, "now", str(self.repo), "../escape")

        real = Path(self.temp.name) / "real"
        real.mkdir()
        linked = Path(self.temp.name) / "linked"
        linked.symlink_to(real, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "must not be a symlink"):
            sessions.create_control_session(linked, "now", str(self.repo), "cs-4444444444444444")

        current = sessions.create_control_session(
            self.base, "now", str(self.repo), "cs-5555555555555555"
        )
        path = sessions.control_session_path(self.base, current["session_id"])
        payload = json.loads(path.read_text())
        payload["schema_version"] = 2
        path.write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, "unsupported control session schema"):
            sessions.load_control_session(self.base, current["session_id"], str(self.repo))


if __name__ == "__main__":
    unittest.main()
