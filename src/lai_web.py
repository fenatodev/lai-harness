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


def web_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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
    }

