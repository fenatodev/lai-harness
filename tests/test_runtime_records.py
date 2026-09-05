import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "src" / "local-agent"
SPEC = importlib.util.spec_from_loader(
    "lai_runtime_records_agent",
    SourceFileLoader("lai_runtime_records_agent", str(SOURCE)),
)
agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent)


class RuntimeRecordsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.old_root = agent.ROOT
        self.old_state = agent.STATE_BASE
        self.old_metrics_dir = agent.METRICS_DIR
        self.old_metrics_file = agent.METRICS_FILE
        self.old_audit_dir = agent.AUDIT_DIR
        self.old_audit_file = agent.AUDIT_FILE
        self.old_metric_max = agent.METRICS_MAX_BYTES
        self.old_metric_keep = agent.METRICS_KEEP_LINES
        self.old_audit_max = agent.AUDIT_MAX_BYTES
        self.old_audit_keep = agent.AUDIT_KEEP_LINES
        self.old_state_days = agent.STATE_RETENTION_DAYS
        agent.ROOT = self.repo.resolve()
        agent.STATE_BASE = self.base / "data" / "state"
        agent.METRICS_DIR = self.base / "data" / "metrics"
        agent.METRICS_FILE = agent.METRICS_DIR / "events.jsonl"
        agent.AUDIT_DIR = self.base / "data" / "audit"
        agent.AUDIT_FILE = agent.AUDIT_DIR / "events.jsonl"

    def tearDown(self):
        agent.ROOT = self.old_root
        agent.STATE_BASE = self.old_state
        agent.METRICS_DIR = self.old_metrics_dir
        agent.METRICS_FILE = self.old_metrics_file
        agent.AUDIT_DIR = self.old_audit_dir
        agent.AUDIT_FILE = self.old_audit_file
        agent.METRICS_MAX_BYTES = self.old_metric_max
        agent.METRICS_KEEP_LINES = self.old_metric_keep
        agent.AUDIT_MAX_BYTES = self.old_audit_max
        agent.AUDIT_KEEP_LINES = self.old_audit_keep
        agent.STATE_RETENTION_DAYS = self.old_state_days
        self.temp.cleanup()

    def test_runtime_json_schemas_are_version_one_draft_2020_12(self):
        schema_dir = ROOT / "schemas" / "runtime"
        expected = {
            "metric_event.schema.json",
            "audit_event.schema.json",
            "workspace_state.schema.json",
            "checkpoint.schema.json",
        }
        self.assertEqual({path.name for path in schema_dir.glob("*.json")}, expected)
        for name in sorted(expected):
            with self.subTest(name=name):
                document = json.loads((schema_dir / name).read_text())
                self.assertEqual(
                    document["$schema"],
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertEqual(document["properties"]["schema_version"]["const"], 1)

    def test_new_metric_and_audit_events_are_versioned(self):
        agent.record_metric_event({"type": "smoke"})
        agent.record_audit_event({"type": "smoke"})
        metric = json.loads(agent.METRICS_FILE.read_text())
        audit = json.loads(agent.AUDIT_FILE.read_text())
        self.assertEqual(metric["schema_version"], 1)
        self.assertEqual(audit["schema_version"], 1)

    def test_jsonl_reader_accepts_legacy_and_skips_future_records(self):
        path = self.base / "events.jsonl"
        records = [
            {"type": "legacy", "run_id": "old"},
            {"schema_version": 1, "type": "current", "run_id": "new"},
            {"schema_version": 2, "type": "future", "run_id": "future"},
        ]
        path.write_text("\n".join(json.dumps(item) for item in records) + "\n")
        loaded = agent.load_jsonl_tail(path)
        self.assertEqual([item["type"] for item in loaded], ["legacy", "current"])

    def test_workspace_state_migrates_legacy_and_rejects_future_version(self):
        json_path, _ = agent.workspace_state_paths()
        json_path.parent.mkdir(parents=True)
        json_path.write_text(json.dumps({
            "root": str(agent.ROOT),
            "last_task": "legacy",
        }))
        legacy = agent.load_workspace_state()
        self.assertEqual(legacy["schema_version"], 1)
        self.assertEqual(legacy["last_task"], "legacy")

        json_path.write_text(json.dumps({
            "schema_version": 2,
            "root": str(agent.ROOT),
            "last_task": "future",
        }))
        future = agent.load_workspace_state()
        self.assertEqual(future["schema_version"], 1)
        self.assertIsNone(future["last_task"])

    def test_retention_config_obeys_precedence_and_validates_bounds(self):
        config = self.base / "config.toml"
        config.write_text(
            "[lai]\n"
            "state_retention_days = 30\n"
            "metrics_max_bytes = 7000\n"
            "metrics_keep_lines = 70\n"
            "audit_max_bytes = 8000\n"
            "audit_keep_lines = 80\n"
        )
        values, _ = agent.load_configuration(
            ["--config", str(config), "--metrics-keep-lines", "90"],
            environ={"LAI_STATE_RETENTION_DAYS": "60"},
            home=self.base,
        )
        self.assertEqual(values["state_retention_days"], 60)
        self.assertEqual(values["metrics_max_bytes"], 7000)
        self.assertEqual(values["metrics_keep_lines"], 90)
        self.assertEqual(values["audit_keep_lines"], 80)

        with self.assertRaisesRegex(SystemExit, "metrics_keep_lines"):
            agent.load_configuration(
                ["--metrics-keep-lines", "0"], environ={}, home=self.base,
            )

    def test_workspace_cleanup_uses_configured_state_retention(self):
        agent.STATE_BASE.mkdir(parents=True)
        stale = agent.STATE_BASE / "stale.json"
        stale_md = stale.with_suffix(".md")
        stale.write_text("{}")
        stale_md.write_text("stale")
        old = __import__("time").time() - 2 * 24 * 60 * 60
        __import__("os").utime(stale, (old, old))
        __import__("os").utime(stale_md, (old, old))
        agent.STATE_RETENTION_DAYS = 1
        agent.cleanup_stale_workspace_states()
        self.assertFalse(stale.exists())
        self.assertFalse(stale_md.exists())

    def test_jsonl_retention_keeps_configured_tail_atomically(self):
        path = self.base / "events.jsonl"
        path.write_text("one\ntwo\nthree\nfour\n")
        changed = agent.prune_jsonl_tail(path, max_bytes=1, keep_lines=2)
        self.assertTrue(changed)
        self.assertEqual(path.read_text(), "three\nfour\n")
        self.assertFalse(any(path.parent.glob("*.retention.tmp")))

    def test_metric_and_audit_writers_use_configured_retention(self):
        agent.METRICS_MAX_BYTES = 1
        agent.METRICS_KEEP_LINES = 1
        agent.AUDIT_MAX_BYTES = 1
        agent.AUDIT_KEEP_LINES = 1
        agent.METRICS_DIR.mkdir(parents=True)
        agent.AUDIT_DIR.mkdir(parents=True)
        agent.METRICS_FILE.write_text('{"type":"old-1"}\n{"type":"old-2"}\n')
        agent.AUDIT_FILE.write_text('{"type":"old-1"}\n{"type":"old-2"}\n')
        agent.record_metric_event({"type": "new"})
        agent.record_audit_event({"type": "new"})
        metrics = [json.loads(line) for line in agent.METRICS_FILE.read_text().splitlines()]
        audit = [json.loads(line) for line in agent.AUDIT_FILE.read_text().splitlines()]
        self.assertEqual([item["type"] for item in metrics], ["old-2", "new"])
        self.assertEqual([item["type"] for item in audit], ["old-2", "new"])


if __name__ == "__main__":
    unittest.main()
