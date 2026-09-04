# Local control plane

`lai serve` exposes a small authenticated HTTP/JSON control surface for local integrations such as a future `lai-gateway`, mobile UI, or private Tailscale proxy.

Beta.13 keeps the server loopback-only and exposes bounded asynchronous model execution for five read-only modes: `plan`, `review`, `security`, `diagnose`, and `release`. Every control child receives an explicit shell-free capability profile before the model sees tool schemas. It is still not a remote shell and it does not expose llama.cpp directly.

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

The server accepts IPv4 loopback (`127.0.0.0/8`) or `localhost` only. Public, LAN, tailnet, and arbitrary hostname binds are rejected. A private proxy should terminate the remote connection and forward to the loopback backend.

Every endpoint requires:

```text
Authorization: Bearer <control-api-token>
```

Requests without a valid bearer token receive `401`. Responses use JSON, disable caching, and suppress the default HTTP access log.

## Read-only state endpoints

### `GET /v1/status`

Returns product/repository state, Git status, active spec summary, existing run-history summary, queue state, and explicit capabilities. In beta.13 `model_execution=true`, `shell_execution=false`, and `repository_write=false` for the HTTP surface. The payload also reports `remote_tool_profile=shell-free-read-only` and the allowed remote modes.

### `GET /v1/readiness`

Reuses the deterministic `lai readiness` collector. It may probe the configured llama.cpp `/props` endpoint but does not itself request a completion.

### `GET /v1/runs?limit=N`

Returns up to 50 sanitized historical run summaries from the existing observability store. This route remains the historical list endpoint.

### `POST /v1/policy-check`

Classifies one tool request through the same deterministic `ALLOW` / `ASK` / `DENY` policy used by the harness. It always returns `executed: false`.

## Asynchronous control runs

### `POST /v1/runs`

Accepts exactly:

```json
{
  "mode": "plan",
  "task": "inspect the repository and propose the next safe change"
}
```

Allowed modes in beta.13:

- `plan`;
- `review`;
- `security`;
- `diagnose`;
- `release`.

The task must be non-empty and at most 4000 characters. Unknown fields are rejected. The client cannot supply an executable, shell command, cwd, argv prefix, or environment override.

Accepted work returns `202` with a generated `control_run_id`. One worker serializes model use and at most four additional requests may wait in the queue. A full queue returns `429`.

The worker launches the current `local-agent` with a fixed argv, `shell=False`, `cwd` fixed to the server repository, stdin disabled, and inherited trusted process configuration. Each child gets its own process group for scoped cancellation. Control-run children never auto-start the model service: if llama.cpp is offline, the run fails cleanly and service startup remains an explicit boot/operations responsibility. Output is captured outside the repository and only a bounded terminal tail is retained in memory.

### `GET /v1/runs/<control_run_id>`

Returns the control-run lifecycle:

- `queued`;
- `running`;
- `succeeded`;
- `failed`;
- `cancelled`.

The record includes task length, timestamps, queue position when applicable, exit code, bounded stdout/stderr, and explicit truncation flags. The full submitted task is not persisted as a new control-plane transcript record.

### `DELETE /v1/runs/<control_run_id>`

Cancels only that queued/running control run. A queued run is cancelled before spawn; a running child is terminated and escalated to kill after a short grace period if needed. The route does not delete Git refs, files, run history, metrics, or audit evidence.

## Remote capability profiles

Local `diagnose` and `release` still retain their existing `bash` tool. Control children do not. When the fixed internal control-child marker is present, the harness intersects the normal local mode tools with an explicit remote profile before building the model request.

For remote `diagnose` and `release`, the model receives only `project`, `read`, `inspect`, `search`, `list`, and `git`. `bash`, `edit`, `create`, `patch`, and `rewrite` are absent from the schema. `plan`, `review`, and `security` remain limited to their existing shell-free inspection tools.

This is capability reduction, not a claim that the local `bash` policy is a sandbox. Shell-capable remote validation remains out of scope until a stronger structured executor is justified.

## Explicitly not exposed

Beta.12 has no HTTP endpoint for:

- arbitrary shell or Git commands;
- file create/patch/rewrite operations;
- `general`, `implement`, `fix`, `ci-fix`, `refactor`, `debug`, or `test` agent runs;
- approvals for `ASK` operations;
- release/tag/push/publication actions;
- package installation or OS administration.

## Intended mobile architecture

```text
phone -> Telegram/PWA -> lai-gateway -> private proxy -> 127.0.0.1:8765 -> lai harness
```

`lai-gateway` is intentionally a separate project. Telegram/WhatsApp credentials, mobile sessions, notification delivery, and commercial/social automation do not belong in the harness core.
