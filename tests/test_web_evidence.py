from __future__ import annotations

import socket
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import lai_web as web  # noqa: E402


PUBLIC_V4 = "93.184.216.34"
PUBLIC_V6 = "2606:2800:220:1:248:1893:25c8:1946"


def public_answers(*ips: str):
    answers = []
    for value in ips:
        if ":" in value:
            answers.append((socket.AF_INET6, socket.SOCK_STREAM, 6, "", (value, 443, 0, 0)))
        else:
            answers.append((socket.AF_INET, socket.SOCK_STREAM, 6, "", (value, 443)))
    return answers


class FakeResponse:
    def __init__(self, *, status=200, body=b"ok", content_type="text/plain; charset=utf-8", encoding="identity"):
        self.status = status
        self._body = body
        self._headers = {
            "Content-Type": content_type,
            "Content-Encoding": encoding,
        }

    def getheader(self, name):
        return self._headers.get(name)

    def read(self, amount=None):
        if amount is None:
            return self._body
        return self._body[:amount]


class FakeConnection:
    response = FakeResponse()
    calls = []

    def __init__(self, host, ip, *, timeout):
        self.host = host
        self.ip = ip
        self.timeout = timeout
        self.connected_ip = ip

    def request(self, method, path, headers=None):
        type(self).calls.append((method, path, dict(headers or {})))

    def getresponse(self):
        return type(self).response

    def close(self):
        return None


class WebEvidenceTest(unittest.TestCase):
    def setUp(self):
        FakeConnection.calls = []
        FakeConnection.response = FakeResponse()

    def test_url_validation_requires_https_443_no_credentials_and_public_dns(self):
        invalid = [
            "http://example.com/",
            "https://user:pass@example.com/",
            "https://example.com:444/",
            "https://127.0.0.1/",
            "https://10.0.0.1/",
            "https://169.254.169.254/latest/meta-data/",
            "file:///etc/passwd",
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                web.validate_web_url(value)

        with mock.patch.object(
            web.socket,
            "getaddrinfo",
            return_value=public_answers(PUBLIC_V4, PUBLIC_V6),
        ):
            destination = web.validate_web_url(
                "https://Example.COM/docs?q=one#ignored-fragment"
            )
        self.assertEqual(destination["url"], "https://example.com/docs?q=one")
        self.assertEqual(destination["path"], "/docs?q=one")
        self.assertEqual(destination["resolved_ips"], [PUBLIC_V4, PUBLIC_V6])

    def test_dns_fails_closed_if_any_answer_is_non_public(self):
        mixed = public_answers(PUBLIC_V4) + public_answers("10.0.0.8")
        with mock.patch.object(web.socket, "getaddrinfo", return_value=mixed):
            with self.assertRaisesRegex(ValueError, "not globally routable"):
                web.validate_web_url("https://example.com/")

    def test_pinned_connection_uses_validated_ip_and_original_hostname_for_tls(self):
        class RawSocket:
            def close(self):
                pass

        class WrappedSocket:
            def getpeername(self):
                return (PUBLIC_V4, 443)

            def close(self):
                pass

        raw = RawSocket()
        wrapped = WrappedSocket()
        context = mock.Mock()
        context.wrap_socket.return_value = wrapped
        with mock.patch.object(web.ssl, "create_default_context", return_value=context), \
                mock.patch.object(web.socket, "create_connection", return_value=raw) as create:
            connection = web._PinnedHTTPSConnection(
                "example.com", PUBLIC_V4, timeout=3.0
            )
            connection.connect()
        create.assert_called_once_with((PUBLIC_V4, 443), 3.0)
        context.wrap_socket.assert_called_once_with(raw, server_hostname="example.com")
        self.assertEqual(connection.connected_ip, PUBLIC_V4)

    def test_fetch_is_get_only_header_minimal_bounded_and_untrusted(self):
        html_body = b"<html><style>secret-style</style><body><h1>Hello</h1><script>bad()</script><p>world</p></body></html>"
        FakeConnection.response = FakeResponse(body=html_body, content_type="text/html; charset=utf-8")
        with mock.patch.object(web, "resolve_public_host", return_value=[PUBLIC_V4]), \
                mock.patch.object(web, "_PinnedHTTPSConnection", FakeConnection), \
                mock.patch.object(web, "web_now", return_value="2026-09-06T02:00:00Z"):
            result = web.fetch_web_evidence("https://example.com/path?q=1", max_chars=200)
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["connected_ip"], PUBLIC_V4)
        self.assertEqual(result["resolved_ips"], [PUBLIC_V4])
        self.assertTrue(result["untrusted_external_content"])
        self.assertEqual(result["egress"]["kind"], "public_fetch")
        self.assertEqual(result["egress"]["decision"], "ALLOW")
        self.assertTrue(result["egress"]["evidence_only"])
        self.assertIn("Hello", result["text"])
        self.assertIn("world", result["text"])
        self.assertNotIn("bad()", result["text"])
        self.assertNotIn("secret-style", result["text"])
        self.assertEqual(len(result["sha256"]), 64)
        method, path, headers = FakeConnection.calls[0]
        self.assertEqual(method, "GET")
        self.assertEqual(path, "/path?q=1")
        self.assertNotIn("Authorization", headers)
        self.assertNotIn("Cookie", headers)
        self.assertEqual(headers["Accept-Encoding"], "identity")

    def test_fetch_rejects_redirect_binary_compressed_and_oversized_responses(self):
        cases = [
            FakeResponse(status=302, body=b"redirect", content_type="text/html"),
            FakeResponse(body=b"binary", content_type="application/octet-stream"),
            FakeResponse(body=b"gzip", content_type="text/plain", encoding="gzip"),
            FakeResponse(body=b"x" * (web.WEB_MAX_BODY_BYTES + 1), content_type="text/plain"),
        ]
        for response in cases:
            FakeConnection.response = response
            with self.subTest(status=response.status, content_type=response.getheader("Content-Type")), \
                    mock.patch.object(web, "resolve_public_host", return_value=[PUBLIC_V4]), \
                    mock.patch.object(web, "_PinnedHTTPSConnection", FakeConnection):
                with self.assertRaises(ValueError):
                    web.fetch_web_evidence("https://example.com/")

    def test_search_parser_decodes_redirect_targets_deduplicates_and_bounds(self):
        body = b"""
        <div class="result">
          <a class="result-link" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fa%3Fx%3D1">First &amp; result</a>
          <a class="result-snippet">First snippet text</a>
        </div>
        <div class="result">
          <a class="result-link" href="https://example.org/b">Second result</a>
          <div class="result-snippet">Second snippet</div>
        </div>
        <div class="result">
          <a class="result-link" href="https://example.org/b">Duplicate</a>
        </div>
        """
        results = web.parse_duckduckgo_results(body, 5)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "First & result")
        self.assertEqual(results[0]["url"], "https://example.com/a?x=1")
        self.assertEqual(results[0]["snippet"], "First snippet text")
        self.assertEqual(results[1]["url"], "https://example.org/b")

    def test_search_rejects_provider_challenge_status(self):
        FakeConnection.response = FakeResponse(
            status=202, body=b"challenge", content_type="text/html"
        )
        with mock.patch.object(web, "resolve_public_host", return_value=[PUBLIC_V4]), \
                mock.patch.object(web, "_PinnedHTTPSConnection", FakeConnection):
            with self.assertRaisesRegex(ValueError, "non-result HTTP status 202"):
                web.search_web_evidence("safe coding harness")

    def test_search_uses_single_fixed_provider_request_and_does_not_fetch_results(self):
        body = b'<a class="result-link" href="https://example.org/a">Example</a><div class="result-snippet">Snippet</div>'
        FakeConnection.response = FakeResponse(body=body, content_type="text/html")
        with mock.patch.object(web, "resolve_public_host", return_value=[PUBLIC_V4]), \
                mock.patch.object(web, "_PinnedHTTPSConnection", FakeConnection), \
                mock.patch.object(web, "web_now", return_value="2026-09-06T02:00:00Z"):
            result = web.search_web_evidence("safe coding harness", max_results=3)
        self.assertEqual(result["provider"], "duckduckgo-lite")
        self.assertEqual(result["result_count"], 1)
        self.assertTrue(result["untrusted_external_content"])
        self.assertEqual(result["egress"]["kind"], "public_search")
        self.assertEqual(result["egress"]["destination_identity"], web.WEB_SEARCH_HOST)
        self.assertEqual(len(FakeConnection.calls), 1)
        method, path, headers = FakeConnection.calls[0]
        self.assertEqual(method, "GET")
        self.assertTrue(path.startswith("/lite/?q=safe+coding+harness"))
        self.assertEqual(headers["Host"], web.WEB_SEARCH_HOST)
        self.assertNotIn("Cookie", headers)
        self.assertNotIn("Authorization", headers)

    def test_egress_broker_grants_are_quota_bound_revocable_and_destination_scoped(self):
        clock = {"now": 10.0}
        broker = web.EgressBroker(now=lambda: clock["now"])
        registry = broker.create_grant(
            "registry",
            audience="tests",
            allowed_hosts=["registry.example"],
            quota=1,
            ttl_seconds=60,
        )
        with mock.patch.object(web, "resolve_public_host", return_value=[PUBLIC_V4]):
            receipt = broker.authorize(
                registry["grant_id"],
                kind="registry",
                destination="https://registry.example/packages/demo",
            )
        self.assertEqual(receipt["reason_code"], "egress_grant_consumed")
        self.assertEqual(receipt["quota_used"], 1)
        self.assertEqual(receipt["destination_identity"], "registry.example")
        with self.assertRaisesRegex(ValueError, "quota exhausted"), \
                mock.patch.object(web, "resolve_public_host", return_value=[PUBLIC_V4]):
            broker.authorize(
                registry["grant_id"],
                kind="registry",
                destination="https://registry.example/packages/demo",
            )

        service = broker.create_grant(
            "local_service",
            audience="tests",
            allowed_urls=["http://127.0.0.1:18181/api/"],
            quota=2,
            ttl_seconds=60,
        )
        service_receipt = broker.authorize(
            service["grant_id"],
            kind="local_service",
            destination="http://127.0.0.1:18181/api/status",
        )
        self.assertEqual(service_receipt["kind"], "local_service")
        self.assertFalse(service_receipt["untrusted_external_content"])
        with self.assertRaisesRegex(ValueError, "outside the egress grant"):
            broker.authorize(
                service["grant_id"],
                kind="local_service",
                destination="http://127.0.0.1:18181/other",
            )
        broker.revoke(service["grant_id"])
        with self.assertRaisesRegex(ValueError, "revoked"):
            broker.authorize(
                service["grant_id"],
                kind="local_service",
                destination="http://127.0.0.1:18181/api/status",
            )

    def test_egress_status_and_proxy_scrubbing_are_secret_free(self):
        payload = web.egress_status_payload()
        self.assertEqual(payload["schema_version"], web.EGRESS_SCHEMA_VERSION)
        self.assertIn("registry_without_grant", payload["denied_by_default"])
        self.assertIn("control_api", payload["denied_by_default"])
        self.assertTrue(payload["evidence_only"])
        cleaned = web.scrub_proxy_environment({
            "PATH": "/bin",
            "HTTPS_PROXY": "http://proxy-secret.example",
            "no_proxy": "127.0.0.1",
        })
        self.assertEqual(cleaned, {"PATH": "/bin"})

    def test_local_service_url_validation_blocks_unregistered_lan_and_metadata(self):
        valid = web.validate_local_service_url("http://localhost:8123/api?q=1")
        self.assertEqual(valid, "http://localhost:8123/api?q=1")
        for value in (
            "http://10.0.0.5:8123/api",
            "http://169.254.169.254:80/latest/meta-data/",
            "http://example.com:8123/api",
            "http://user:pass@127.0.0.1:8123/api",
            "file:///tmp/service",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                web.validate_local_service_url(value)


if __name__ == "__main__":
    unittest.main()
