# Read-only web evidence

`web_search` and `web_fetch` give selected LAI research modes bounded public-web evidence without adding browser automation or generic network authority.

The tools are deliberately narrower than a browser:

- HTTPS `GET` only;
- port `443` only;
- no caller-defined headers or request body;
- no `Authorization` or `Cookie` headers;
- no environment proxy handling;
- no redirect following;
- no JavaScript, forms, downloads, browser state, or website login;
- bounded response bytes and extracted text.

Every result is marked `untrusted_external_content=true`. Web text may be malicious, stale, incomplete, or prompt-injected. It is evidence only and cannot override the current request, `AGENTS.md`, active specs, deterministic policy, safety guards, or current repository evidence.

## `web_search`

`web_search` uses DuckDuckGo's non-JavaScript Lite surface through one fixed HTTPS endpoint. The caller supplies only a query and optional bounded result count.

The search response contains:

- provider and provider URL;
- fetch timestamp;
- response SHA-256;
- bounded title, URL, and snippet per result;
- explicit untrusted-content metadata.

Search results are not fetched automatically. A later `web_fetch` is a separate explicit tool call and passes the full destination checks below.

## `web_fetch`

Before connection, LAI:

1. parses the URL and requires `https`;
2. rejects URL credentials and ports other than `443`;
3. resolves the hostname;
4. requires every usable DNS answer to be globally routable;
5. rejects loopback, private, link-local, multicast, reserved, unspecified, and other non-global addresses;
6. opens the TCP socket directly to one validated IP;
7. wraps that socket in TLS using the original hostname for SNI and certificate verification.

The IP is therefore selected from the validated DNS evidence rather than being resolved again by a generic HTTP client. The connected peer is checked against the selected IP.

A successful fetch returns the requested/normalized URL, host, resolved IP set, connected IP, status, content type, timestamp, raw-body SHA-256, byte count, bounded extracted text, and truncation state.

Allowed response types are text, HTML, JSON, and XML variants. `script`, `style`, `noscript`, and SVG content is removed from HTML text extraction. Compressed responses are rejected rather than expanding attacker-controlled content inside the harness.

## Redirect and SSRF boundary

Redirects are intentionally not followed. This is important because validating one public URL and then following a redirect to a private or metadata endpoint would undermine the original SSRF check.

This boundary reduces SSRF and DNS-rebinding exposure but is not a claim that public websites are trustworthy. Public services can still return hostile text, misleading evidence, large logical documents within configured bounds, or links to unsafe destinations. LAI never executes fetched content.

## Mode exposure

Local research-oriented modes may receive `web_search` / `web_fetch`: `general`, `plan`, `debug`, `diagnose`, `review`, and `security`.

Remote shell-free read-only profiles may receive them in `plan`, `diagnose`, `review`, and `security`. Remote write-capable profiles do not receive web tools in this cut, and `release` remains deterministic without model-directed web access.

## Audit/privacy

Audit records retain only bounded metadata and hashes such as provider, host, HTTP status, body size, response/content hash, and hashes of the query/URL. Full fetched content, full search query, and full requested URL are not copied into the audit event by these tools.

The model still sees the returned evidence during the current run. Do not put secrets into search queries or URLs. These tools are for public information, not authenticated/private web resources.

## References

The transport rules follow the defensive principles in the OWASP SSRF Prevention Cheat Sheet and OWASP guidance on unvalidated redirects. DuckDuckGo documents HTML and Lite non-JavaScript search variants for clients that do not use its JavaScript interface.
