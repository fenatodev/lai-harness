import importlib.util
from importlib.machinery import SourceFileLoader
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "src" / "local-agent"
SPEC = importlib.util.spec_from_loader(
    "lai_update_intelligence_agent",
    SourceFileLoader("lai_update_intelligence_agent", str(SOURCE)),
)
agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent)


class FakeHeaders:
    def __init__(self, content_type="application/json", length=None):
        self.content_type = content_type
        self.length = length

    def get_content_type(self):
        return self.content_type

    def get(self, name):
        return self.length if name == "Content-Length" else None


class FakeResponse:
    def __init__(self, body, url, content_type="application/json", length=None):
        self.body = body
        self.url = url
        self.headers = FakeHeaders(content_type, length)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def geturl(self):
        return self.url

    def read(self, limit=-1):
        return self.body if limit < 0 else self.body[:limit]


class FakeOpener:
    def __init__(self, response):
        self.response = response

    def open(self, request, timeout=None):
        return self.response


class UpdateIntelligenceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.old_root = agent.ROOT
        self.old_data = agent.DATA_BASE
        agent.ROOT = self.repo.resolve()
        agent.DATA_BASE = self.base / "data"

    def tearDown(self):
        agent.ROOT = self.old_root
        agent.DATA_BASE = self.old_data
        self.temp.cleanup()

    def test_version_classifier_distinguishes_updates_and_manual_review(self):
        self.assertEqual(agent.classify_update_version("1.2.3", "1.2.3"), "current")
        self.assertEqual(agent.classify_update_version("1.2.3", "1.2.4"), "update_available")
        self.assertEqual(agent.classify_update_version("1.2.4", "1.2.3"), "ahead_of_latest")
        self.assertEqual(
            agent.classify_update_version("b10730", "v0.4.0"),
            "version_changed_manual_review",
        )

    def test_http_helper_rejects_untrusted_scheme_and_host(self):
        for url in (
            "http://pypi.org/pypi/ruff/json",
            "https://example.com/data.json",
            "https://user:pass@pypi.org/pypi/ruff/json",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                agent.update_http_json(url)

    def test_http_helper_rejects_redirect_escape_and_invalid_payloads(self):
        cases = [
            FakeResponse(b"{}", "https://evil.example/result"),
            FakeResponse(b"not-json", "https://pypi.org/pypi/ruff/json"),
            FakeResponse(b"{}", "https://pypi.org/pypi/ruff/json", "text/html"),
            FakeResponse(
                b"{}", "https://pypi.org/pypi/ruff/json",
                length=str(agent.UPDATE_MAX_RESPONSE_BYTES + 1),
            ),
        ]
        for response in cases:
            with self.subTest(response=response.url), \
                    mock.patch.object(agent.urllib.request, "build_opener", return_value=FakeOpener(response)):
                with self.assertRaises(ValueError):
                    agent.update_http_json("https://pypi.org/pypi/ruff/json")

    def test_pypi_source_surfaces_exact_version_vulnerabilities(self):
        source = {
            "id": "ruff", "category": "dev-sensor", "source_type": "pypi",
            "package": "ruff", "current_detector": "dev-pin", "current_version": "1.0.0",
            "security_source": "pypi-release",
        }
        responses = [
            {"info": {"version": "1.1.0"}},
            {"vulnerabilities": [{"id": "PYSEC-1", "details": "example issue", "fixed_in": ["1.0.1"]}]},
        ]
        with mock.patch.object(agent, "update_http_json", side_effect=responses), \
                mock.patch.object(agent, "update_source_current_version", return_value="1.0.0"):
            result = agent.check_update_pypi_source(source)
        self.assertEqual(result["status"], "update_available")
        self.assertEqual(result["security_status"], "vulnerable")
        self.assertEqual(result["vulnerability_count"], 1)
        self.assertEqual(result["vulnerabilities"][0]["id"], "PYSEC-1")
        self.assertEqual(result["vulnerabilities"][0]["fixed_in"], ["1.0.1"])

    def test_github_release_uses_canonical_url_and_bounded_untrusted_body(self):
        source = {
            "id": "qwen-code", "category": "reference-agent", "source_type": "github-release",
            "repository": "QwenLM/qwen-code", "current_detector": "none", "security_source": "none",
        }
        body = "X" * 5000
        payload = {
            "tag_name": "v9.9.9",
            "name": "Release 9.9.9",
            "published_at": "2026-09-05T00:00:00Z",
            "body": body,
            "html_url": "https://evil.example/phish",
        }
        with mock.patch.object(agent, "update_http_json", return_value=payload):
            result = agent.check_update_github_release_source(source)
        self.assertEqual(result["status"], "observed")
        self.assertEqual(
            result["source_url"],
            "https://github.com/QwenLM/qwen-code/releases/tag/v9.9.9",
        )
        self.assertEqual(result["release_notes_sha256"], hashlib.sha256(body.encode()).hexdigest())
        self.assertLessEqual(len(result["release_notes_excerpt"]), 1600)
        self.assertEqual(result["content_trust"], "untrusted-upstream-release-notes")

    def test_manifest_plan_is_offline_and_fail_closed(self):
        manifest = agent.load_update_sources()
        self.assertFalse(manifest["policy"]["automatic_apply"])
        self.assertFalse(manifest["policy"]["arbitrary_urls"])
        with mock.patch.object(agent, "update_http_json", side_effect=AssertionError("network used")):
            rendered = agent.render_update_plan(json_mode=True)
        payload = json.loads(rendered)
        self.assertEqual(payload["network"], "disabled")
        self.assertTrue(any(item["id"] == "mypy" for item in payload["sources"]))

    def test_remote_check_persists_and_detects_change_without_repo_mutation(self):
        manifest = {
            "schema_version": 1, "manifest_sha256": "a" * 64,
            "policy": {"automatic_apply": False, "arbitrary_urls": False, "reference_upstreams_are_dependencies": False},
            "sources": [{
                "id": "tool", "category": "harness-tool", "source_type": "npm",
                "package": "tool", "current_detector": "none", "security_source": "none",
            }],
        }
        snapshot = {"head": "abc123", "status": ""}
        first_record = {
            "id": "tool", "category": "harness-tool", "source_type": "npm",
            "current_version": "1.0.0", "latest_version": "1.0.0", "status": "current",
            "security_status": "unknown", "vulnerability_count": None, "vulnerabilities": [],
            "source_url": "https://www.npmjs.com/package/tool", "content_trust": "trusted-metadata-untrusted-text",
        }
        with mock.patch.object(agent, "load_update_sources", return_value=manifest), \
                mock.patch.object(agent, "update_workspace_snapshot", return_value=snapshot), \
                mock.patch.object(agent, "check_update_source", return_value=dict(first_record)):
            first = agent.run_update_check()
        self.assertIsNone(first["sources"][0]["changed_since_last_check"])
        self.assertTrue(Path(first["result_path"]).is_file())
        self.assertEqual(json.loads(Path(first["latest_path"]).read_text())["result_path"], first["result_path"])
        changed_record = dict(first_record)
        changed_record.update({"latest_version": "1.1.0", "status": "update_available"})
        with mock.patch.object(agent, "load_update_sources", return_value=manifest), \
                mock.patch.object(agent, "update_workspace_snapshot", return_value=snapshot), \
                mock.patch.object(agent, "check_update_source", return_value=changed_record):
            second = agent.run_update_check()
        self.assertTrue(second["sources"][0]["changed_since_last_check"])
        self.assertEqual(second["update_candidates"], ["tool"])
        latest = json.loads(Path(second["latest_path"]).read_text())
        self.assertEqual(latest["check_id"], second["check_id"])
        self.assertEqual(agent.render_update_latest(json_mode=True).strip()[0], "{")

    def test_remote_check_fails_if_workspace_changes(self):
        manifest = {
            "schema_version": 1, "manifest_sha256": "b" * 64,
            "policy": {"automatic_apply": False, "arbitrary_urls": False, "reference_upstreams_are_dependencies": False},
            "sources": [],
        }
        snapshots = [{"head": "a", "status": ""}, {"head": "b", "status": ""}]
        with mock.patch.object(agent, "load_update_sources", return_value=manifest), \
                mock.patch.object(agent, "update_workspace_snapshot", side_effect=snapshots):
            with self.assertRaisesRegex(ValueError, "repository changed"):
                agent.run_update_check()

    def test_llama_build_detector_parses_authenticated_props_or_returns_unknown(self):
        payload = json.dumps({"build_info": "b10730-abcdef"}).encode()
        response = FakeResponse(payload, "http://127.0.0.1:8080/props")
        with mock.patch.object(agent.urllib.request, "urlopen", return_value=response), \
                mock.patch.object(agent, "gateway", return_value="127.0.0.1"), \
                mock.patch.object(agent, "llama_api_key", return_value="secret"):
            self.assertEqual(agent.update_llama_cpp_build(), "b10730")
        with mock.patch.object(agent.urllib.request, "urlopen", side_effect=OSError("offline")):
            self.assertIsNone(agent.update_llama_cpp_build())

    def test_cli_surface_has_no_apply_install_or_download_operation(self):
        for command in ("apply", "install", "download", "upgrade", "pr", "merge"):
            with self.subTest(command=command), self.assertRaises(SystemExit):
                agent.handle_update_intelligence([command])
        with self.assertRaisesRegex(SystemExit, "requires explicit --remote"):
            agent.handle_update_intelligence(["check"])
        with self.assertRaisesRegex(SystemExit, "local-only"):
            agent.handle_update_intelligence(["latest", "--remote"])


    def test_source_checkout_manifest_matches_canonical_pins(self):
        old_root = agent.ROOT
        try:
            agent.ROOT = ROOT.resolve()
            manifest = agent.load_update_sources()
        finally:
            agent.ROOT = old_root
        by_id = {item["id"]: item for item in manifest["sources"]}
        self.assertEqual(by_id["mypy"]["current_version"], "2.3.1")
        self.assertEqual(by_id["pytest"]["current_version"], "9.1.1")
        self.assertEqual(by_id["ruff"]["current_version"], "0.16.6")
        self.assertEqual(by_id["harness-score"]["current_version"], "1.6.3")

    def test_http_helper_sends_no_public_feed_credentials_and_bounds_body(self):
        class CapturingOpener(FakeOpener):
            request = None
            def open(self, request, timeout=None):
                self.request = request
                return self.response
        response = FakeResponse(b"123456", "https://pypi.org/pypi/ruff/json")
        opener = CapturingOpener(response)
        with mock.patch.object(agent, "UPDATE_MAX_RESPONSE_BYTES", 4), \
                mock.patch.object(agent.urllib.request, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "size limit"):
                agent.update_http_json("https://pypi.org/pypi/ruff/json")
        headers = {key.lower(): value for key, value in opener.request.header_items()}
        self.assertNotIn("authorization", headers)
        self.assertNotIn("cookie", headers)

    def test_update_result_retention_is_bounded_and_ignores_latest(self):
        result_dir = self.base / "data" / "update-intelligence"
        result_dir.mkdir(parents=True)
        for index in range(4):
            path = result_dir / f"20260905T00000{index}Z-run.json"
            path.write_text("{}\n")
        (result_dir / "latest.json").write_text("{}\n")
        agent.prune_update_intelligence_results(result_dir, keep=2)
        retained = sorted(path.name for path in result_dir.glob("*.json"))
        self.assertEqual(len(retained), 3)
        self.assertIn("latest.json", retained)
        self.assertIn("20260905T000003Z-run.json", retained)
        self.assertIn("20260905T000002Z-run.json", retained)

if __name__ == "__main__":
    unittest.main()
