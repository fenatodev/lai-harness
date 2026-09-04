# Local control plane

`lai serve` exposes a small HTTP/JSON control surface for local integrations such as a future `lai-gateway`, mobile UI, or private Tailscale proxy.

Beta.11 deliberately keeps this API read-only with respect to model execution and repository mutation. It is not a remote shell and it does not expose llama.cpp.

## Initialize authentication

The control plane uses its own bearer token, separate from the llama.cpp API key:

```bash
lai control-token init
lai control-token status
```

The default token file is `$LAI_CONFIG_DIR/control-api-key`, normally `~/.config/lai/control-api-key`. Initialization uses cryptographically secure randomness, writes mode `0600`, and does not print the secret. Existing tokens are not overwritten unless `--force` is explicit.

Override the location with `LAI_CONTROL_API_KEY_FILE`, `control_api_key_file` in `[lai]`, or the leading `--control-api-key-file` configuration option.

## Start the API

```bash
lai serve
lai serve --bind 127.0.0.1 --port 8765
```

Beta.11 accepts loopback only (`127.0.0.0/8` or `localhost`). `0.0.0.0`, LAN addresses, tailnet addresses, and arbitrary hostnames are rejected. This is intentional: a private proxy such as Tailscale Serve should terminate the remote connection and forward to the loopback backend instead of making lai listen directly on another interface.

Every endpoint requires:

```text
Authorization: Bearer <control-api-token>
```

Requests without a valid bearer token receive `401`. Responses use JSON, disable caching, and the handler suppresses the default HTTP access log.

## Endpoints

### `GET /v1/status`

Returns lightweight local state:

- product/version and repository path;
- Git branch/status/clean flag;
- active spec summary;
- run count and latest public run summary;
- explicit capabilities showing model, shell, and repository-write execution are disabled over HTTP.

### `GET /v1/readiness`

Reuses the deterministic `lai readiness` collector. It may probe the configured llama.cpp `/props` endpoint but never asks the model to generate a completion.

### `GET /v1/runs?limit=N`

Returns up to 50 public run-history summaries using the existing sanitized run-history view.

### `POST /v1/policy-check`

Classifies one tool request through the same deterministic `ALLOW` / `ASK` / `DENY` policy used by the harness. It always returns `executed: false`.

Example request body:

```json
{
  "tool": "bash",
  "args": {"command": "git status --short"},
  "mode": "review"
}
```

## Explicitly not exposed

Beta.11 has no HTTP endpoint for:

- arbitrary shell or Git commands;
- file create/patch/rewrite operations;
- model prompts or write-capable agent modes;
- approvals for `ASK` operations;
- release/tag/push/publication actions;
- package installation or OS administration.

Those capabilities require a separate design because a mobile control surface changes the trust boundary. A later beta can add asynchronous agent runs and explicit approval objects without weakening the existing policy gateway.

## Intended mobile architecture

```text
phone -> Telegram/PWA -> lai-gateway -> private proxy -> 127.0.0.1:8765 -> lai harness
```

`lai-gateway` is intentionally a separate project. Telegram/WhatsApp credentials, mobile sessions, notification delivery, and social/business automation do not belong in the harness core.
