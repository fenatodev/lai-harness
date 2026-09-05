# Local control plane

`lai serve` exposes a small authenticated HTTP/JSON control surface for local integrations such as `lai-gateway`, a private PWA, Telegram, or a Tailscale proxy.

Beta.15 keeps the server loopback-only and supports two explicit run classes plus a separate approved-promotion action:

- shell-free read-only runs: `plan`, `review`, `security`, `diagnose`, `release`;
- isolated work runs: `implement`, `fix`, `refactor`, `ci-fix`.

Work runs never execute directly in the source checkout. Each gets a disposable safe workspace copied from tracked repository contents. The model can use repository-confined file tools plus structured `validate`, but never generic `bash` or Git mutation tools. Validation executes in a constrained Docker sandbox. A successful run may later expose a hash-bound promotion proposal; promotion is deterministic and creates a dedicated feature worktree rather than editing the active checkout.

![LAI private mobile access architecture](assets/private-mobile-access.png)

The `lai-gateway` layer shown above is a separate companion project; it is not shipped by lai harness.

## Initialize authentication

The control plane uses its own bearer token, separate from the llama.cpp API key:

```bash
lai control-token init
lai control-token status
```

The default token file is `$LAI_CONFIG_DIR/control-api-key`, normally `~/.config/lai/control-api-key`. Initialization uses cryptographically secure randomness, writes mode `0600`, and does not print the secret. Existing tokens are not overwritten unless `--force` is explicit.

## Start the API

```bash
lai serve
lai serve --bind 127.0.0.1 --port 8765
```

The server accepts IPv4 loopback (`127.0.0.0/8`) or `localhost` only. Public, LAN, tailnet, and arbitrary hostname binds are rejected. A private gateway/proxy should terminate the remote connection and forward to the loopback backend.

Every endpoint requires:

```text
Authorization: Bearer <control-api-token>
```

Requests without a valid bearer token receive `401`. Responses use JSON, disable caching, and suppress the default HTTP access log.

## State endpoints

### `GET /v1/status`

Returns product/repository state, Git status, active spec summary, historical-run summary, queue state, and explicit capabilities.

Beta.15 reports `model_execution=true`, `shell_execution=false`, and `repository_write=false` for the source checkout. It also reports `sandbox_workspace_write=true`, `async_work_runs=true`, the configured validation sandbox image, sandbox readiness, and the allowed remote modes.

`repository_write=false` is deliberate: a remote work run can mutate only its disposable safe workspace. Beta.15 additionally reports `approved_workspace_promotion=true` with `promotion_target=dedicated-feature-worktree`; promotion creates a separate Git worktree/branch and still does not edit the active source checkout.

### `GET /v1/readiness`

Reuses the deterministic `lai readiness` collector. It may probe the configured llama.cpp `/props` endpoint but does not itself request a completion.

### `GET /v1/runs?limit=N`

Returns up to 50 sanitized historical run summaries from the existing observability store. This remains the historical list endpoint.

### `POST /v1/policy-check`

Classifies one tool request through the same deterministic `ALLOW` / `ASK` / `DENY` policy used by the harness. It always returns `executed: false`.

## Asynchronous control runs

### `POST /v1/runs`

Accepts exactly:

```json
{
  "mode": "implement",
  "task": "add the requested regression test and validate the change"
}
```

Allowed run modes in beta.15:

- read-only: `plan`, `review`, `security`, `diagnose`, `release`;
- work: `implement`, `fix`, `refactor`, `ci-fix`.

The task must be non-empty and at most 4000 characters. Unknown fields are rejected. The client cannot supply an executable, shell command, cwd, argv prefix, environment override, validation command, container image, or Docker options.

Accepted work returns `202` with a generated `control_run_id`. One worker serializes model use and at most four additional requests may wait in the queue. A full queue returns `429`.

Control-run children use fixed argv, `shell=False`, disabled stdin, a dedicated process group, and trusted inherited configuration. They never auto-start the model service: if llama.cpp is offline, the run fails cleanly and service startup remains an explicit operations responsibility.

### Read-only runs

Read-only runs execute against the source checkout with capability-reduced inspection tools. They cannot receive write tools or `bash`.

### Work runs

Before spawning a work child, the control plane creates a unique safe workspace under the configured safe-workspace base. Only tracked source-repository contents are copied, the workspace gets its own isolated Git branch, and the child process uses that workspace as its repository root.

Remote work profiles expose repository-confined read/write tools plus `validate`; `bash` and Git mutation tools are absent. Existing path confinement, symlink rejection, stale-write protection, `AGENTS.md` handling, spec requirements, patch sanity, validation guards, and mode-specific progress guards continue to apply inside the isolated workspace.

When the child terminates, the control plane records a bounded workspace Git status, changed-path list, and diff. The source checkout is not modified.

### Approved promotion

`GET /v1/runs/<control_run_id>/promotion` computes a read-only proposal. Only a `succeeded` work run with a clean, unchanged source baseline and a non-empty safe patch can become `promotable`. The server inventories paths with NUL-delimited Git output, builds the complete bounded binary-capable patch, and returns its SHA-256, size, changed paths, source SHA/branch, and deterministic target branch. Display diffs are not used as approval material.

`POST /v1/runs/<control_run_id>/promotion` accepts exactly `{"patch_sha256":"<64 lowercase hex>"}`. The server compares that hash to freshly recomputed patch bytes, repeats the repository `full` validation profile in the same networkless Docker sandbox, rechecks source SHA/branch/clean state, and then creates `lai/promotion-<run-id>` in a durable Git worktree under the LAI data directory. It runs `git apply --check` before `git apply`, recomputes the promoted worktree patch, and requires the resulting SHA-256 to match the approved hash.

Failed/cancelled runs, source drift, dirty source state, mutable workspace-metadata drift, oversized/unsafe patches, validation failure, hash mismatch, or an existing target branch/worktree all fail closed. Repeating the same successful approval is idempotent. Promotion does not commit, push, merge, switch the active checkout, or call the model.

### Structured validation

`validate` accepts only a profile, not a command:

```json
{"profile":"test"}
```

Profiles are `test`, `check`, `lint`, `build`, `typecheck`, and `full`. The harness selects a recognized existing project command from Makefile targets, package scripts, or conservative language-native project metadata. If no recognized command exists, validation fails closed; it never falls back to caller-supplied shell.

For control-run work children, validation executes through a fixed Docker invocation with:

- `--pull=never`;
- `--network=none`;
- read-only container root;
- `--cap-drop=ALL` and `no-new-privileges`;
- bounded CPU, memory, and process count;
- no host `$HOME`;
- no Docker socket;
- only the work workspace writable;
- explicitly recognized runtime/dependency mounts read-only when needed.

The harness never pulls a sandbox image automatically. If Docker or the configured local sandbox image is unavailable, a work run is rejected before model execution.

### `GET /v1/runs/<control_run_id>`

Returns `queued`, `running`, `succeeded`, `failed`, or `cancelled` plus timestamps, exit code, bounded stdout/stderr, truncation flags, and the tool-profile name.

For work runs it additionally returns the isolated workspace path, bounded Git status, changed paths, bounded diff, and a diff-truncation flag. The full submitted task is not persisted as a new control-plane transcript record.

### `DELETE /v1/runs/<control_run_id>`

Cancels only that queued/running control run. A queued run is cancelled before spawn; a running child is terminated and escalated to kill after a short grace period if needed. The route does not delete Git refs, source files, historical run records, metrics, or audit evidence.

## Explicitly not exposed

Beta.15 still has no HTTP capability for:

- arbitrary shell or arbitrary executable invocation;
- direct writes to or branch switching of the active source checkout;
- commit, push, merge, tag, release publication, or caller-selected Git mutation;
- dependency/package installation;
- Docker control chosen by the model/caller;
- OS/service administration;
- caller-controlled environment, cwd, mount, image, or network options.

## Intended mobile architecture

```text
phone -> Telegram/PWA -> lai-gateway -> Tailscale/private proxy -> 127.0.0.1:8765 -> lai harness
                                                        |-> read-only run
                                                        `-> isolated work workspace -> sandbox validate -> patch hash
                                                                                         -> approved promotion -> feature worktree
```

`lai-gateway` is intentionally a separate project. Messaging credentials, mobile sessions, notification delivery, and commercial/social automation do not belong in the harness core.
