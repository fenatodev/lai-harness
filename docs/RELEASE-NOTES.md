# Release notes

## lai harness v0.4.0-beta.11 — local control plane foundation

This beta creates the safe local API boundary needed for future smartphone access without turning lai harness into a network-exposed shell or embedding messaging platforms into the core.

### What changed

- Added `lai control-token init|status` with a control-plane secret separate from the llama.cpp API key.
- Token initialization uses cryptographically secure randomness, writes mode `0600`, refuses silent overwrite, and does not print the secret.
- Added `lai serve`, implemented with Python's standard library only.
- The server binds only to IPv4 loopback/`localhost` in beta.11; public, LAN, and tailnet bind addresses are rejected.
- Every API endpoint requires bearer authentication.
- Added `GET /v1/status`, `GET /v1/readiness`, `GET /v1/runs`, and `POST /v1/policy-check`.
- Added bounded JSON request handling, content-type checks, structured errors, connection timeout, no-store responses, and suppressed default access logging.
- Added explicit capability reporting that model execution, shell execution, and repository writes are disabled over HTTP.
- Added focused server/token tests and an installed `lai serve` smoke test.

### Why this matters

The intended mobile architecture is no longer "expose llama.cpp" or "let Telegram run shell". The harness now has a narrow local control boundary that a separate gateway can consume. A private proxy such as Tailscale Serve can later forward to loopback while the harness itself remains bound to localhost.

This separation also protects project scope: `lai-gateway` will own Telegram/PWA/mobile transport, while business/social automation remains a separate product that can be developed and dogfooded with lai harness.

### Safety boundary

- No HTTP endpoint executes a model prompt.
- No HTTP endpoint executes shell or Git commands.
- No HTTP endpoint writes repository files.
- `POST /v1/policy-check` classifies only and always returns `executed: false`.
- Unsupported methods and endpoints fail with controlled JSON responses.
- The control token is a separate trust domain from the model-server token.
- `lai serve` refuses non-loopback binding in this beta.

### Validation gate

```bash
lai control-token status --json
lai release-check --target 0.4.0-beta.11 --json
lai release-pack --target 0.4.0-beta.11 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

### Release body for GitHub

lai harness v0.4.0-beta.11 adds an authenticated, loopback-only local control plane for future mobile integrations. `lai serve` exposes narrow JSON status/readiness/run-history/policy endpoints while explicitly disabling model execution, shell execution, and repository writes over HTTP.

A separate `lai control-token` lifecycle keeps control-plane authentication independent from llama.cpp. The implementation uses Python's standard library, refuses non-loopback binds, limits request bodies, returns structured JSON errors, and includes installed-wrapper smoke coverage. Messaging/PWA adapters remain outside the harness core by design.
