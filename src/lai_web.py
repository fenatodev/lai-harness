from __future__ import annotations

import hashlib
import html
import http.client
import ipaddress
import socket
import ssl
import time
import urllib.parse
from html.parser import HTMLParser
from collections.abc import Callable, Mapping
from typing import TypedDict


WEB_TIMEOUT_SECONDS = 8.0
WEB_MAX_BODY_BYTES = 256 * 1024
WEB_DEFAULT_TEXT_CHARS = 12000
WEB_MAX_TEXT_CHARS = 20000
WEB_SEARCH_MAX_QUERY_CHARS = 500
WEB_SEARCH_MAX_RESULTS = 8
WEB_SEARCH_DEFAULT_RESULTS = 5
WEB_SEARCH_HOST = "lite.duckduckgo.com"
WEB_SEARCH_PATH = "/lite/"
WEB_USER_AGENT = "lai-harness/0.4 read-only-web-evidence"
WEB_ALLOWED_CONTENT_TYPES = frozenset({
    "text/plain",
    "text/html",
    "application/json",
    "application/ld+json",
    "application/xml",
    "text/xml",
})
EGRESS_SCHEMA_VERSION = 1
EGRESS_BROKER_SCHEMA_VERSION = 1
EGRESS_MAX_QUOTA = 20
EGRESS_KINDS = frozenset({
    "offline", "public_search", "public_fetch", "registry", "local_service",
})
EGRESS_PROXY_ENV_NAMES = frozenset({
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "all_proxy", "no_proxy",
})
EGRESS_PUBLIC_EVIDENCE_GRANT_ID = "eg-public-evidence-implicit"


class EgressReceipt(TypedDict):
    schema_version: int
    decision: str
    reason_code: str
    grant_id: str
    kind: str
    operation: str
    destination: str
    destination_identity: str
    quota_used: int
    quota_total: int
    evidence_only: bool
    untrusted_external_content: bool
    trust: str


class EgressGrantRecord(TypedDict):
    schema_version: int
    grant_id: str
    kind: str
    audience: str
    allowed_hosts: list[str]
    allowed_urls: list[str]
    quota_total: int
    quota_used: int
    created_at: float
    expires_at: float
    revoked: bool
    evidence_only: bool


class EgressStatus(TypedDict):
    schema_version: int
    default_policy: str
    evidence_only: bool
    supported_kinds: list[str]
    implicit_public_evidence_kinds: list[str]
    denied_by_default: list[str]
    proxy_environment_blocked: list[str]
    trust: str


class WebDestination(TypedDict):
    url: str
    host: str
    port: int
    path: str
    resolved_ips: list[str]


class WebFetchEvidence(TypedDict):
    requested_url: str
    url: str
    host: str
    resolved_ips: list[str]
    connected_ip: str
    status: int
    content_type: str
    fetched_at: str
    sha256: str
    body_bytes: int
    text: str
    truncated: bool
    untrusted_external_content: bool
    egress: EgressReceipt


class WebSearchResult(TypedDict):
    title: str
    url: str
    snippet: str


class WebSearchEvidence(TypedDict):
    query: str
    provider: str
    provider_url: str
    resolved_ips: list[str]
    connected_ip: str
    status: int
    fetched_at: str
    result_count: int
    results: list[WebSearchResult]
    response_sha256: str
    untrusted_external_content: bool
    egress: EgressReceipt


class RawWebResponse(TypedDict):
    requested_url: str
    url: str
    host: str
    resolved_ips: list[str]
    connected_ip: str
    status: int
    content_type: str
    fetched_at: str
    raw: bytes
    egress: EgressReceipt


def web_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def egress_status_payload() -> EgressStatus:
    return {
        "schema_version": EGRESS_SCHEMA_VERSION,
        "default_policy": "deny_by_default_except_implicit_public_web_evidence",
        "evidence_only": True,
        "supported_kinds": sorted(EGRESS_KINDS),
        "implicit_public_evidence_kinds": ["public_fetch", "public_search"],
        "denied_by_default": [
            "lan", "loopback", "metadata_service", "model_backend",
            "control_api", "registry_without_grant", "local_service_without_grant",
            "browser_automation", "authenticated_external_action",
        ],
        "proxy_environment_blocked": sorted(EGRESS_PROXY_ENV_NAMES),
        "trust": (
            "Egress grants authorize a destination class and quota only; "
            "allowed domains are not proof that returned content is safe or non-exfiltrating."
        ),
    }


def scrub_proxy_environment(source: Mapping[str, str]) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in source.items()
        if str(key) not in EGRESS_PROXY_ENV_NAMES and str(key).upper() not in EGRESS_PROXY_ENV_NAMES
    }


def _normalize_egress_host(host: object) -> str:
    if not isinstance(host, str) or not host.strip():
        raise ValueError("egress host must be a non-empty string")
    try:
        normalized = host.strip().encode("idna").decode("ascii").rstrip(".").lower()
    except UnicodeError as exc:
        raise ValueError("invalid egress host") from exc
    if not normalized or len(normalized) > 253:
        raise ValueError("invalid egress host")
    return normalized


def _validate_loopback_literal_or_localhost(host: str) -> str:
    clean = _normalize_egress_host(host)
    if clean == "localhost":
        return clean
    try:
        address = ipaddress.ip_address(clean)
    except ValueError as exc:
        raise ValueError("local service host must be localhost or a loopback IP literal") from exc
    if not address.is_loopback:
        raise ValueError("local service host is not loopback")
    return address.compressed


def validate_local_service_url(url: object) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("local service URL must be a non-empty URL")
    raw = url.strip()
    if len(raw) > 4096:
        raise ValueError("local service URL is too long")
    try:
        parsed = urllib.parse.urlsplit(raw)
    except ValueError as exc:
        raise ValueError("invalid local service URL") from exc
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("local service URL must use http or https")
    if parsed.hostname is None:
        raise ValueError("local service URL must include a host")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("credentials in local service URLs are not allowed")
    host = _validate_loopback_literal_or_localhost(parsed.hostname)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid local service URL port") from exc
    if port is None or port <= 0 or port > 65535:
        raise ValueError("local service URL must include a valid explicit port")
    path = parsed.path or "/"
    if not path.startswith("/"):
        raise ValueError("invalid local service URL path")
    netloc = f"{host}:{port}"
    if ":" in host and not host.startswith("["):
        netloc = f"[{host}]:{port}"
    return urllib.parse.urlunsplit((parsed.scheme.lower(), netloc, path, parsed.query, ""))


def _egress_public_receipt(kind: str, destination: str, identity: str, operation: str) -> EgressReceipt:
    if kind not in {"public_fetch", "public_search"}:
        raise ValueError("implicit egress receipt is only available for public web evidence")
    return {
        "schema_version": EGRESS_SCHEMA_VERSION,
        "decision": "ALLOW",
        "reason_code": "implicit_public_web_evidence",
        "grant_id": EGRESS_PUBLIC_EVIDENCE_GRANT_ID,
        "kind": kind,
        "operation": operation,
        "destination": destination,
        "destination_identity": identity,
        "quota_used": 1,
        "quota_total": 1,
        "evidence_only": True,
        "untrusted_external_content": True,
        "trust": "Destination governance is not content trust; treat all response text as untrusted evidence.",
    }


class EgressBroker:
    def __init__(self, now: Callable[[], float] | None = None) -> None:
        self._now = now or time.time
        self._grants: dict[str, EgressGrantRecord] = {}
        self._counter = 0

    def _next_grant_id(self, kind: str, audience: str) -> str:
        self._counter += 1
        seed = f"{kind}:{audience}:{self._counter}:{self._now():.9f}"
        return "eg-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]

    def create_grant(
        self,
        kind: str,
        *,
        audience: str,
        allowed_hosts: list[str] | None = None,
        allowed_urls: list[str] | None = None,
        quota: int = 1,
        ttl_seconds: int = 300,
    ) -> EgressGrantRecord:
        clean_kind = str(kind or "").strip().lower()
        if clean_kind not in EGRESS_KINDS:
            raise ValueError("unsupported egress kind")
        clean_audience = str(audience or "").strip()
        if not clean_audience or len(clean_audience) > 160:
            raise ValueError("egress audience must be a bounded non-empty string")
        if not isinstance(quota, int) or quota < 0 or quota > EGRESS_MAX_QUOTA:
            raise ValueError(f"egress quota must be between 0 and {EGRESS_MAX_QUOTA}")
        if not isinstance(ttl_seconds, int) or ttl_seconds < 1 or ttl_seconds > 3600:
            raise ValueError("egress ttl_seconds must be between 1 and 3600")
        hosts = [_normalize_egress_host(item) for item in (allowed_hosts or [])]
        urls = [validate_local_service_url(item) for item in (allowed_urls or [])]
        if clean_kind == "offline":
            quota = 0
            hosts = []
            urls = []
        elif clean_kind == "public_search":
            hosts = [WEB_SEARCH_HOST]
            urls = []
            quota = max(1, quota)
        elif clean_kind in {"public_fetch", "registry"} and not hosts:
            raise ValueError(f"{clean_kind} egress grant requires allowed_hosts")
        elif clean_kind == "local_service" and not urls:
            raise ValueError("local_service egress grant requires allowed_urls")
        created = self._now()
        record: EgressGrantRecord = {
            "schema_version": EGRESS_BROKER_SCHEMA_VERSION,
            "grant_id": self._next_grant_id(clean_kind, clean_audience),
            "kind": clean_kind,
            "audience": clean_audience,
            "allowed_hosts": sorted(set(hosts)),
            "allowed_urls": sorted(set(urls)),
            "quota_total": quota,
            "quota_used": 0,
            "created_at": created,
            "expires_at": created + ttl_seconds,
            "revoked": False,
            "evidence_only": True,
        }
        self._grants[record["grant_id"]] = record
        return record.copy()

    def revoke(self, grant_id: str) -> EgressGrantRecord:
        record = self._grants.get(str(grant_id or ""))
        if record is None:
            raise ValueError("unknown egress grant")
        record["revoked"] = True
        return record.copy()

    def _destination_for_kind(self, kind: str, destination: object) -> tuple[str, str]:
        if kind == "offline":
            raise ValueError("offline grant does not authorize egress")
        if kind == "local_service":
            url = validate_local_service_url(destination)
            parsed = urllib.parse.urlsplit(url)
            return url, parsed.netloc.lower() + (parsed.path or "/")
        web_destination = validate_web_url(destination)
        return web_destination["url"], web_destination["host"]

    def authorize(
        self,
        grant_id: str,
        *,
        kind: str,
        destination: object,
        operation: str = "GET",
    ) -> EgressReceipt:
        record = self._grants.get(str(grant_id or ""))
        if record is None:
            raise ValueError("egress grant not found")
        clean_kind = str(kind or "").strip().lower()
        if clean_kind != record["kind"]:
            raise ValueError("egress kind does not match grant")
        if record["revoked"]:
            raise ValueError("egress grant is revoked")
        if self._now() > float(record["expires_at"]):
            raise ValueError("egress grant expired")
        if int(record["quota_used"]) >= int(record["quota_total"]):
            raise ValueError("egress quota exhausted")
        destination_url, identity = self._destination_for_kind(clean_kind, destination)
        if clean_kind == "public_search" and identity != WEB_SEARCH_HOST:
            raise ValueError("public_search egress is pinned to the search provider")
        if clean_kind in {"public_fetch", "registry"} and identity not in set(record["allowed_hosts"]):
            raise ValueError("destination host is outside the egress grant")
        if clean_kind == "local_service":
            prefixes = [urllib.parse.urlsplit(item).netloc.lower() + (urllib.parse.urlsplit(item).path or "/") for item in record["allowed_urls"]]
            if not any(identity.startswith(prefix) for prefix in prefixes):
                raise ValueError("local service destination is outside the egress grant")
        record["quota_used"] = int(record["quota_used"]) + 1
        return {
            "schema_version": EGRESS_SCHEMA_VERSION,
            "decision": "ALLOW",
            "reason_code": "egress_grant_consumed",
            "grant_id": record["grant_id"],
            "kind": clean_kind,
            "operation": str(operation or "GET")[:40],
            "destination": destination_url,
            "destination_identity": identity,
            "quota_used": int(record["quota_used"]),
            "quota_total": int(record["quota_total"]),
            "evidence_only": True,
            "untrusted_external_content": clean_kind != "local_service",
            "trust": "A matching egress grant is not proof of response safety, correctness, or non-exfiltration.",
        }

    def snapshot(self) -> dict[str, object]:
        return {
            "schema_version": EGRESS_BROKER_SCHEMA_VERSION,
            "grant_count": len(self._grants),
            "grants": [dict(item) for item in sorted(self._grants.values(), key=lambda row: row["grant_id"])],
            "evidence_only": True,
        }


def _public_ip(value: str) -> str:
    try:
        address = ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValueError("destination resolved to an invalid IP address") from exc
    if not address.is_global:
        raise ValueError(f"destination IP is not globally routable: {address.compressed}")
    return address.compressed


def resolve_public_host(host: str, port: int = 443) -> list[str]:
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        return [_public_ip(literal.compressed)]

    try:
        answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise ValueError(f"DNS resolution failed for {host}") from exc
    resolved: list[str] = []
    for family, socktype, _proto, _canonname, sockaddr in answers:
        if socktype != socket.SOCK_STREAM or family not in {socket.AF_INET, socket.AF_INET6}:
            continue
        ip = _public_ip(str(sockaddr[0]))
        if ip not in resolved:
            resolved.append(ip)
    if not resolved:
        raise ValueError(f"DNS resolution returned no usable public address for {host}")
    return resolved


def validate_web_url(url: object) -> WebDestination:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty HTTPS URL")
    raw = url.strip()
    if len(raw) > 4096:
        raise ValueError("url is too long")
    try:
        parsed = urllib.parse.urlsplit(raw)
    except ValueError as exc:
        raise ValueError("invalid URL") from exc
    if parsed.scheme.lower() != "https":
        raise ValueError("only HTTPS URLs are allowed")
    if not parsed.netloc or parsed.hostname is None:
        raise ValueError("HTTPS URL must include a hostname")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("credentials in URLs are not allowed")
    try:
        port = parsed.port or 443
    except ValueError as exc:
        raise ValueError("invalid URL port") from exc
    if port != 443:
        raise ValueError("only HTTPS port 443 is allowed")
    try:
        host = parsed.hostname.encode("idna").decode("ascii").rstrip(".").lower()
    except UnicodeError as exc:
        raise ValueError("invalid hostname") from exc
    if not host or len(host) > 253:
        raise ValueError("invalid hostname")
    path = parsed.path or "/"
    if not path.startswith("/"):
        raise ValueError("invalid URL path")
    request_path = path + (("?" + parsed.query) if parsed.query else "")
    normalized = urllib.parse.urlunsplit(("https", host, path, parsed.query, ""))
    return {
        "url": normalized,
        "host": host,
        "port": 443,
        "path": request_path,
        "resolved_ips": resolve_public_host(host, 443),
    }


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host: str, ip: str, *, timeout: float) -> None:
        context = ssl.create_default_context()
        super().__init__(host=host, port=443, timeout=timeout, context=context)
        self._validated_ip = ip
        self._lai_context = context
        self.connected_ip = ""

    def connect(self) -> None:
        raw = socket.create_connection(
            (self._validated_ip, self.port),
            self.timeout,
        )
        try:
            self.sock = self._lai_context.wrap_socket(raw, server_hostname=self.host)
        except BaseException:
            raw.close()
            raise
        peer = self.sock.getpeername()[0]
        self.connected_ip = _public_ip(str(peer))
        if ipaddress.ip_address(self.connected_ip) != ipaddress.ip_address(self._validated_ip):
            self.close()
            raise OSError("connected peer differs from validated destination")


class _VisibleHTMLText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._hidden_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._hidden_depth += 1
        elif self._hidden_depth == 0 and tag.lower() in {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._hidden_depth:
            self._hidden_depth -= 1
        elif self._hidden_depth == 0 and tag.lower() in {"p", "div", "li", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._hidden_depth == 0:
            self.parts.append(data)

    def text(self) -> str:
        lines = [" ".join(line.split()) for line in "".join(self.parts).splitlines()]
        return "\n".join(line for line in lines if line)


def extract_web_text(body: bytes, content_type: str) -> str:
    charset = "utf-8"
    media_type = content_type.split(";", 1)[0].strip().lower()
    for item in content_type.split(";")[1:]:
        key, sep, value = item.strip().partition("=")
        if sep and key.lower() == "charset" and value.strip():
            charset = value.strip().strip('"').strip("'")[:40]
    try:
        decoded = body.decode(charset, errors="replace")
    except LookupError:
        decoded = body.decode("utf-8", errors="replace")
    if media_type == "text/html":
        parser = _VisibleHTMLText()
        parser.feed(decoded)
        parser.close()
        return parser.text()
    return decoded.replace("\x00", " ").strip()


def _bounded_text(text: str, max_chars: int) -> tuple[str, bool]:
    normalized = text.strip()
    if len(normalized) <= max_chars:
        return normalized, False
    return normalized[: max(0, max_chars - 1)] + "…", True


def _request_web_bytes(
    url: object,
    *,
    timeout: float = WEB_TIMEOUT_SECONDS,
    accept: str = "text/html,text/plain,application/json,application/xml;q=0.8,*/*;q=0.1",
    egress_kind: str = "public_fetch",
) -> RawWebResponse:
    destination = validate_web_url(url)
    last_error: BaseException | None = None
    for ip in destination["resolved_ips"]:
        connection = _PinnedHTTPSConnection(destination["host"], ip, timeout=timeout)
        try:
            connection.request(
                "GET",
                destination["path"],
                headers={
                    "Host": destination["host"],
                    "User-Agent": WEB_USER_AGENT,
                    "Accept": accept,
                    "Accept-Encoding": "identity",
                    "Connection": "close",
                },
            )
            response = connection.getresponse()
            if 300 <= response.status < 400:
                raise ValueError("redirect responses are not followed")
            if response.status < 200 or response.status >= 300:
                raise ValueError(f"HTTP status {response.status}")
            encoding = (response.getheader("Content-Encoding") or "identity").strip().lower()
            if encoding not in {"", "identity"}:
                raise ValueError("compressed web responses are not accepted")
            content_type = (response.getheader("Content-Type") or "").strip()
            media_type = content_type.split(";", 1)[0].strip().lower()
            if media_type not in WEB_ALLOWED_CONTENT_TYPES:
                raise ValueError(f"unsupported content type: {media_type or '[missing]'}")
            raw = response.read(WEB_MAX_BODY_BYTES + 1)
            if len(raw) > WEB_MAX_BODY_BYTES:
                raise ValueError("web response body exceeds size limit")
            return {
                "requested_url": str(url).strip(),
                "url": destination["url"],
                "host": destination["host"],
                "resolved_ips": list(destination["resolved_ips"]),
                "connected_ip": connection.connected_ip or ip,
                "status": response.status,
                "content_type": content_type,
                "fetched_at": web_now(),
                "raw": raw,
                "egress": _egress_public_receipt(
                    egress_kind, destination["url"], destination["host"], "GET"
                ),
            }
        except (OSError, ssl.SSLError, http.client.HTTPException, ValueError) as exc:
            last_error = exc
            if isinstance(exc, ValueError):
                raise
        finally:
            connection.close()
    raise ValueError(f"HTTPS connection failed: {type(last_error).__name__ if last_error else 'unknown'}")


def fetch_web_evidence(
    url: object,
    *,
    max_chars: int = WEB_DEFAULT_TEXT_CHARS,
    timeout: float = WEB_TIMEOUT_SECONDS,
) -> WebFetchEvidence:
    if not isinstance(max_chars, int) or not 200 <= max_chars <= WEB_MAX_TEXT_CHARS:
        raise ValueError(f"max_chars must be between 200 and {WEB_MAX_TEXT_CHARS}")
    response = _request_web_bytes(url, timeout=timeout)
    extracted = extract_web_text(response["raw"], response["content_type"])
    text, text_truncated = _bounded_text(extracted, max_chars)
    return {
        "requested_url": response["requested_url"],
        "url": response["url"],
        "host": response["host"],
        "resolved_ips": response["resolved_ips"],
        "connected_ip": response["connected_ip"],
        "status": response["status"],
        "content_type": response["content_type"],
        "fetched_at": response["fetched_at"],
        "sha256": hashlib.sha256(response["raw"]).hexdigest(),
        "body_bytes": len(response["raw"]),
        "text": text,
        "truncated": text_truncated,
        "untrusted_external_content": True,
        "egress": response["egress"],
    }


class _DuckDuckGoHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.results: list[WebSearchResult] = []
        self._title_href: str | None = None
        self._title_parts: list[str] = []
        self._snippet_parts: list[str] | None = None

    @staticmethod
    def _class_value(attrs: list[tuple[str, str | None]]) -> str:
        return next((value or "" for key, value in attrs if key.lower() == "class"), "")

    @staticmethod
    def _href_value(attrs: list[tuple[str, str | None]]) -> str:
        return next((value or "" for key, value in attrs if key.lower() == "href"), "")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = set(self._class_value(attrs).split())
        if tag.lower() == "a" and classes.intersection({"result__a", "result-link"}):
            self._title_href = self._href_value(attrs)
            self._title_parts = []
        elif classes.intersection({"result__snippet", "result-snippet"}) and self.results:
            self._snippet_parts = []

    def handle_data(self, data: str) -> None:
        if self._title_href is not None:
            self._title_parts.append(data)
        elif self._snippet_parts is not None:
            self._snippet_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._title_href is not None:
            title = " ".join("".join(self._title_parts).split())
            href = normalize_search_result_url(self._title_href)
            if title and href:
                self.results.append({"title": html.unescape(title), "url": href, "snippet": ""})
            self._title_href = None
            self._title_parts = []
        elif self._snippet_parts is not None and tag.lower() in {"a", "div", "span"}:
            snippet = " ".join("".join(self._snippet_parts).split())
            if self.results and snippet:
                self.results[-1]["snippet"] = html.unescape(snippet)
            self._snippet_parts = None


def normalize_search_result_url(value: str) -> str:
    href = html.unescape(value.strip())
    if not href:
        return ""
    if href.startswith("//"):
        href = "https:" + href
    parsed = urllib.parse.urlsplit(href)
    if parsed.hostname and parsed.hostname.lower().endswith("duckduckgo.com"):
        query = urllib.parse.parse_qs(parsed.query)
        redirect_target = (query.get("uddg") or [""])[0]
        if redirect_target:
            href = redirect_target
            parsed = urllib.parse.urlsplit(href)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return ""
    if parsed.username is not None or parsed.password is not None:
        return ""
    return urllib.parse.urlunsplit((parsed.scheme.lower(), parsed.netloc, parsed.path or "/", parsed.query, ""))


def parse_duckduckgo_results(body: bytes, max_results: int) -> list[WebSearchResult]:
    parser = _DuckDuckGoHTMLParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    parser.close()
    unique: list[WebSearchResult] = []
    seen: set[str] = set()
    for item in parser.results:
        if item["url"] in seen:
            continue
        seen.add(item["url"])
        item["title"], _ = _bounded_text(item["title"], 300)
        item["snippet"], _ = _bounded_text(item["snippet"], 700)
        unique.append(item)
        if len(unique) >= max_results:
            break
    return unique


def search_web_evidence(
    query: object,
    *,
    max_results: int = WEB_SEARCH_DEFAULT_RESULTS,
    timeout: float = WEB_TIMEOUT_SECONDS,
) -> WebSearchEvidence:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    clean_query = " ".join(query.split())
    if len(clean_query) > WEB_SEARCH_MAX_QUERY_CHARS:
        raise ValueError(f"query must be at most {WEB_SEARCH_MAX_QUERY_CHARS} characters")
    if not isinstance(max_results, int) or not 1 <= max_results <= WEB_SEARCH_MAX_RESULTS:
        raise ValueError(f"max_results must be between 1 and {WEB_SEARCH_MAX_RESULTS}")
    encoded = urllib.parse.urlencode({"q": clean_query, "kl": "wt-wt", "kp": "1"})
    provider_url = f"https://{WEB_SEARCH_HOST}{WEB_SEARCH_PATH}?{encoded}"
    response = _request_web_bytes(
        provider_url,
        timeout=timeout,
        accept="text/html",
        egress_kind="public_search",
    )
    if response["status"] != 200:
        raise ValueError(f"search provider returned non-result HTTP status {response['status']}")
    if not response["content_type"].lower().startswith("text/html"):
        raise ValueError("search provider returned non-HTML content")
    results = parse_duckduckgo_results(response["raw"], max_results)
    return {
        "query": clean_query,
        "provider": "duckduckgo-lite",
        "provider_url": provider_url,
        "resolved_ips": response["resolved_ips"],
        "connected_ip": response["connected_ip"],
        "status": response["status"],
        "fetched_at": response["fetched_at"],
        "result_count": len(results),
        "results": results,
        "response_sha256": hashlib.sha256(response["raw"]).hexdigest(),
        "untrusted_external_content": True,
        "egress": response["egress"],
    }

