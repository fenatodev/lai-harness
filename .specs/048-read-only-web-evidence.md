# Spec: read-only web evidence

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Add bounded read-only web search/fetch evidence for research modes without browser actions, credentials, private-network reachability, redirect following, or any new write authority.

## Requirements

### REQ-001

Add a typed stdlib-only `src/lai_web.py` that performs HTTPS GET through a DNS-resolved public-IP allow decision and a TLS connection pinned to the validated IP/hostname pair.

### REQ-002

Reject non-HTTPS URLs, credentials in URLs, non-443 ports, localhost/private/link-local/multicast/reserved/unspecified destinations, redirects, oversized bodies, unsupported content types, malformed responses, and failed TLS/DNS evidence.

### REQ-003

Provide `web_fetch` evidence with requested URL, host, validated IPs, connected IP, HTTP status, content type, fetch timestamp, SHA-256, bounded extracted text, truncation state, and an explicit `untrusted_external_content=true` marker.

### REQ-004

Provide `web_search` through a fixed DuckDuckGo non-JavaScript HTTPS endpoint, bounded query/result count, no cookies/auth, parsed title/URL/snippet evidence, and no automatic fetching of result pages.

### REQ-005

Expose `web_search` and `web_fetch` only to research-oriented local modes and shell-free remote read-only modes; do not add them to write-capable remote profiles in this cut.

### REQ-006

Install the new module, add semantic navigation and strict-mypy coverage, and document hostile-content/SSRF/privacy boundaries.

### REQ-007

Prove the network boundary with fully mocked DNS/socket/TLS/HTTP regressions before any live dogfood, then run one bounded public search/fetch dogfood only if the deterministic safety tests are green.

## Acceptance Criteria

- Network tools are GET-only and cannot send Authorization/Cookie headers or caller-defined headers/body.
- No redirect is followed; a 3xx response is surfaced as an error/evidence boundary.
- Every DNS answer must be globally routable and the TLS socket connects to one of those validated IPs while authenticating the original hostname.
- Returned external text is bounded and explicitly untrusted; it never becomes policy, spec, or repository evidence by itself.
- Existing repository `search` behavior is unchanged.
- No browser JS, form submission, download-to-disk, MCP, shell, Git mutation, model lifecycle, or dependency installation is added.

## Validation

- `REQ-001`: strict mypy plus pinned-IP connection unit tests.
- `REQ-002`: table-driven SSRF/scheme/port/redirect/type/size failure tests.
- `REQ-003`: deterministic fetch evidence/extraction/hash tests.
- `REQ-004`: fixture-driven DuckDuckGo result parser/search tests.
- `REQ-005`: mode/tool-profile and policy regressions.
- `REQ-006`: install smoke, semantic contract, docs, and mypy ratchet.
- `REQ-007`: no-live-network unit suite first; only then bounded live dogfood and final milestone gate.

## Context and Constraints

OWASP SSRF guidance recommends protocol restrictions, public-address validation, and disabling redirect following because redirects can bypass destination validation. DuckDuckGo documents official non-JavaScript HTML/Lite search surfaces suitable for a browserless GET-only search integration.

## Non-Goals

- No browser automation, JavaScript execution, screenshots, forms, POST/PUT/PATCH/DELETE, file downloads, cookies, authentication, or session persistence for websites.
- No intranet/localhost/cloud-metadata access, custom proxy support, caller-provided DNS/IP override, or custom headers.
- No MCP broker or Desktop Commander integration in this spec.

## Implementation Notes

Prefer a small `http.client.HTTPSConnection` subclass whose socket is opened directly to a previously validated public IP and then wrapped with TLS using the original hostname for SNI/certificate verification. Ignore environment proxy variables by not using urllib request openers. Parse HTML with `html.parser`; remove script/style content and keep text bounded.

## Traceability

- `REQ-001` -> `src/lai_web.py`, network-boundary tests.
- `REQ-002` -> SSRF/redirect/body/content-type tests.
- `REQ-003` -> fetch-evidence tests.
- `REQ-004` -> search parser/provider tests.
- `REQ-005` -> `src/local-agent` tool/profile tests.
- `REQ-006` -> installer, semantic contract, mypy/quality sensors, docs.
- `REQ-007` -> mocked focused suite, bounded dogfood, final milestone gate.

## Validation Evidence

- Added typed stdlib-only `src/lai_web.py` with GET-only public HTTPS fetch/search evidence, bounded body/text extraction, explicit `untrusted_external_content=true`, and no caller-supplied headers, cookies, credentials, request body, redirects, browser automation, or environment proxy use.
- URL and DNS validation rejects non-HTTPS, credentials, non-443 ports, localhost/private/link-local/multicast/reserved/unspecified destinations, invalid DNS answers, redirects, compressed/binary/unsupported responses, oversized bodies, and malformed evidence.
- TLS connections are pinned to a previously validated public IP while using the original hostname for SNI/certificate verification, and the connected peer is checked against the selected validated IP.
- `web_search` uses only the fixed DuckDuckGo Lite HTTPS endpoint, bounds query/result count, parses title/URL/snippet evidence, deduplicates results, and never fetches result pages automatically.
- Tool exposure is restricted to selected research-oriented local modes and shell-free remote read-only profiles; write-capable remote profiles and release mode do not receive web tools.
- Installed runtime now includes `lai_web.py`; semantic navigation points at `web-evidence`; strict mypy ratchet increased to seven files.
- Documentation added hostile-content, SSRF, redirect, privacy, and audit boundaries in `docs/WEB-EVIDENCE.md` and linked mode/control/security docs.
- Focused mocked safety suite passed: 21 web/local-agent tests plus 28 subtests; install/control/quality focus passed: 5 tests; Ruff, strict mypy, and static checks passed.
- Bounded live dogfood after mocked tests succeeded: `https://example.com/` fetched with status 200, globally routable resolved IPs, connected IP `104.20.23.154`, SHA-256 `ff67a9d764d6a2367a187734e697f6a53217db9a21c101d410a113ca871a299d`, 559 body bytes, and `untrusted_external_content=true`; DuckDuckGo Lite search for `OWASP SSRF Prevention Cheat Sheet` returned 3 bounded results with provider status 200, connected IP `191.235.123.80`, response SHA-256 `ee38d557273bcbeb58a9627fe9540ca14cee55e025cf3b47aec48d09b59a160c`, and `untrusted_external_content=true`.
- Full milestone gate passed: 271 pytest tests + 97 subtests, Harness Score L4 100/108 (93%), 271 unittest tests, strict mypy over seven files, publication scan, and VSIX inspection green in 128.76s.
- Public product version remains `0.4.0`; no dependency installation, model lifecycle change, GitHub push, PR, tag, release, or publication mutation occurred for this spec.
