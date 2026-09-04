# Spec: Local control plane foundation

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Expose a small, authenticated, loopback-only HTTP control plane for lai harness so future mobile gateways can query safe local state without exposing llama.cpp or a generic shell surface.

## Requirements

### REQ-001

Add `lai serve` as a dedicated local control API entrypoint implemented with the Python standard library only. It must bind to loopback by default and refuse non-loopback bind addresses in this beta.

### REQ-002

Use a control-plane bearer token separate from the llama.cpp API key. The token file must live under lai config by default, remain configurable, never be rendered by config/status output, and require restrictive file permissions.

### REQ-003

Expose only narrow JSON endpoints in beta.11: authenticated status/readiness, run-history inspection, and policy classification. Do not expose arbitrary shell, Git mutation, file writes, model execution, release publication, or repository mutation through HTTP.

### REQ-004

Return structured JSON errors, enforce request-size limits, reject malformed JSON/content types, avoid secret/token echoing, and emit no default HTTP access log containing authorization material.

### REQ-005

Add a deterministic token-initialization command suitable for unattended boot setup. Initialization must use cryptographically secure randomness, create parent directories safely, write with mode `0600`, and refuse silent overwrite unless explicitly requested.

### REQ-006

Add focused unit/integration coverage proving authentication, loopback-only binding, endpoint allowlisting, malformed-request handling, token-file permission checks, and non-execution of shell/model/write actions.

## Acceptance Criteria

- `lai serve --port 8765` can start on `127.0.0.1` with no third-party Python dependency.
- Requests without the correct bearer token receive `401` and no protected data.
- `lai control-token init` creates a separate secret file with mode `0600` and does not print the secret by default.
- Status/readiness/run-history/policy-check HTTP responses reuse existing deterministic collectors where practical.
- No endpoint accepts a shell command or model prompt for execution in beta.11.

## Validation

- `REQ-001`: server start/bind tests using ephemeral loopback ports plus CLI routing tests.
- `REQ-002` / `REQ-005`: configuration/token lifecycle tests including mode and overwrite behavior.
- `REQ-003`: authenticated endpoint tests for status/readiness/runs/policy and explicit 404/405 rejection for unsupported actions.
- `REQ-004`: request-limit, malformed JSON, media-type, auth, and redaction tests.
- `REQ-006`: focused tests, install smoke, `make lint`, `make check`, `make test-dev`, `make test`, `make harness-score-gate`, and `make validate`.

## Context and Constraints

Beta.10 is released at `v0.4.0-beta.10`. The intended mobile architecture keeps messaging/PWA adapters outside the harness: `lai-gateway` will talk to this local control API, while Tailscale Serve can later proxy the loopback service into the user's private tailnet. Tailscale explicitly recommends localhost-only backends when identity/capability headers are involved.

## Non-Goals

- Do not add Telegram, WhatsApp, Meta, Tailscale, or PWA dependencies to the lai-harness repository.
- Do not expose llama.cpp directly to the LAN/tailnet/public internet.
- Do not implement remote write-capable agent runs or approval workflows in this beta.
- Do not add a generic command-execution endpoint.
- Do not make `lai serve` a requirement for ordinary CLI usage.

## Implementation Notes

Prefer `http.server.ThreadingHTTPServer` / `BaseHTTPRequestHandler`, constant-time bearer comparison, explicit response schemas, and existing deterministic collectors. Keep the control token in a separate trust domain from the llama.cpp API key. A later beta can add asynchronous model runs and `ASK` approval objects once this read-only foundation is proven.

## Traceability

- `REQ-001` -> `src/local-agent`, `src/lai`, server lifecycle tests.
- `REQ-002` / `REQ-005` -> configuration, secret helpers, token CLI and tests.
- `REQ-003` / `REQ-004` -> HTTP handler/routes and endpoint tests.
- `REQ-006` -> install smoke, docs, beta metadata and full validation.
