# Local control plane

For a public navigation entry point, see [Documentation portal](README.md) and [Gateway contract](GATEWAY-CONTRACT.md).


This page documents the implemented v1 control surface after A12. [Target architecture](TARGET-ARCHITECTURE.md) remains a future-planning reference. The current implementation includes scoped authority presets, durable approval intents, local-chat work review, fixture MCP execution, browser fixtures, fake external actions, bounded delegates and distribution/validation diagnostics. Approved arbitrary tool-payload execution, generic MCP `call-tool`, real browser automation and real external-account effects remain disabled.

`lai serve` exposes a small authenticated HTTP/JSON control surface for local integrations such as `lai-gateway`, a private PWA, Telegram, or a Tailscale proxy.

The stable core keeps the server loopback-only and supports persistent repository-scoped sessions, two explicit run classes, and a separate approved-promotion action:

- shell-free read-only runs: `plan`, `review`, `security`, `diagnose`, `release`;
- isolated work runs: `implement`, `fix`, `refactor`, `ci-fix`.

Work runs never execute directly in the source checkout. Each gets a disposable safe workspace copied from tracked repository contents. The model can use repository-confined file tools, structured `validate`, and bounded `sandbox_exec` inside the verified sandbox. It still never receives generic host `bash` or direct source-checkout Git tools. A successful run may later expose a hash-bound promotion proposal; promotion is deterministic and creates a dedicated feature worktree rather than editing the active checkout.

![Gateway and local-chat flow](assets/diagrams/gateway-local-chat.svg)

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

### `GET /v1/gateway-contract`

Returns the stable machine-readable companion-gateway contract: schema version, supported endpoints, bearer-auth expectations, request/run/session limits, run modes, companion responsibilities, and explicit forbidden capabilities. It now advertises the additive local-chat/inspector routes while preserving the v1 legacy authority ceiling. This endpoint is authenticated and contains no bearer tokens, model API keys, host environment variables, private run transcripts, or session turn bodies. The same payload is available locally with `lai gateway-contract --json`; the Linux/WSL bootstrap diagnostic is available with `lai chat-bootstrap --json`, and local distribution/install state is available with `lai distribution status --json`. See [Gateway contract](GATEWAY-CONTRACT.md).

### Local chat and inspector contract

`GET /v1/local-chat/contract?client_version=1` negotiates the local chat/inspector channel. It requires bearer auth plus loopback `Host`; if an `Origin` header is present it must also be loopback. The response returns the supported version, server-registered workspace route, server-approved model route, cursor event route, CSRF header name/token for local POSTs, review/promotion routes, and explicit non-authority flags. The client does not gain path, model, source-write, MCP, approval-execution, direct llama proxy, or host-shell authority from this contract.

`GET /v1/local-chat/workspaces?client_version=1` lists only workspaces registered by the server. In this cut that is the currently served repository, identified by an opaque `lw-<16 hex>` ID and display metadata; it does not expose arbitrary client-provided paths as authority. `GET /v1/local-chat/models?client_version=1&workspace_id=<id>` lists only `model_id=default` as the configured local model choice and does not expose API keys or model paths.

`GET /v1/local-chat/content?client_version=1&workspace_id=<id>&path=<relative-path>` returns bounded UTF-8 text for inspector display after repository confinement, symlink rejection, binary rejection, size limits and token/secret-pattern redaction. It exposes the relative path, not a client-granted absolute path.

`POST /v1/local-chat/runs` requires `X-LAI-CSRF` and accepts only `client_version`, `workspace_id`, `model_id`, `mode`, `task`, and optional `session_id`. Read-only modes enqueue normal read-only control runs. Work modes enqueue the existing A3 verified-sandbox work profile only when the digest-pinned sandbox is ready; otherwise the request fails closed without host fallback. `GET /v1/local-chat/runs/<control_run_id>/events?client_version=1&cursor=N` returns metadata-only trajectory events after the cursor, with no stdout/stderr bodies.

`GET /v1/local-chat/runs/<control_run_id>/review?client_version=1&workspace_id=<id>` returns a sanitized review object for the UI: mode/status/tool profile, lifecycle availability, changed paths, bounded redacted diff preview, promotion proposal, validation state, ASK status and budget projection metadata. It does not include child stdout/stderr, absolute workspace path, secrets, or a replayable tool payload.

`POST /v1/local-chat/runs/<control_run_id>/promotion` requires `X-LAI-CSRF`, `workspace_id` and one exact `patch_sha256`. It delegates to the existing harness promotion path, revalidates patch/source drift, and creates a dedicated promotion worktree/branch when successful. Stale hashes fail with `promotion_conflict`; repeat submission of the same already-promoted hash is idempotent. `POST /v1/local-chat/runs/<control_run_id>/lifecycle` currently supports idempotent `cancel`; `pause` and `continue` are explicit reason-coded non-capabilities until the supervisor implements real paused states.

Unsupported client versions, unsupported channel names, unregistered workspaces, adversarial origins, bad hosts, missing CSRF, unavailable sandbox, stale hashes and unsupported lifecycle actions fail explicitly with reason-coded JSON errors.

### `GET /v1/status`

Returns product/repository state, Git status, active spec summary, historical-run summary, queue state, and explicit capabilities.

The current control surface reports `model_execution=true`, `shell_execution=false`, `repository_write=false`, `persistent_sessions=true`, `scoped_authority_foundation=true`, `durable_approval_intents=true`, `credential_broker_foundation=true`, `real_credentials_enabled=false`, `approved_tool_payload_execution=false`, `verified_sandbox_executor=true`, `verified_sandbox_ready=<bool>`, `distribution_status_cli=true`, `install_upgrade_requires_explicit_script=true`, `automatic_upgrade=false`, `local_chat_contract=true`, `local_chat_read_only_runs=true`, `local_chat_inspector=true`, and `local_chat_work_runs=true` for the source checkout. It also reports `sandbox_workspace_write=true`, `async_work_runs=true`, local-chat work review/promotion routes, the configured digest-pinned sandbox image, sandbox readiness, bounded session limits, and the allowed remote modes.

`repository_write=false` is deliberate: a remote work run can mutate only its disposable safe workspace. The server additionally reports `approved_workspace_promotion=true` with `promotion_target=dedicated-feature-worktree`; promotion creates a separate Git worktree/branch and still does not edit the active source checkout.

### `GET /v1/readiness`

Reuses the deterministic `lai readiness` collector. It may probe the configured llama.cpp `/props` endpoint but does not itself request a completion.

### `GET /v1/runs?limit=N`

Returns up to 50 sanitized in-memory control-run summaries for runs created through the control plane. Each listed item includes `control_run_id`, matching `GET /v1/runs/<control_run_id>`. The local `lai runs` command remains the historical observability view.

### Local distribution state

`lai distribution status [--json]` is a local diagnostic command, not a control-plane write endpoint. It reads `$LAI_DATA_DIR/distribution/installed-state.json` when present and reports installed component metadata, previous version, rollback backup availability, uninstall preservation policy and publication non-effects. Future unknown state schemas fail closed with data preserved. The command does not publish, autoupdate, download models, start another runtime, install optional components or grant Gateway authority to mutate the host.

### Persistent sessions

`POST /v1/sessions` with an empty JSON object creates a repository-scoped session and returns a generated `cs-<16 hex>` identifier. `GET /v1/sessions?limit=N` lists bounded summaries for the currently served repository, `GET /v1/sessions/<session_id>` returns the retained compact turns, and `DELETE /v1/sessions/<session_id>` removes one repository-scoped session. Every route remains bearer-authenticated.

Local operators can inspect and remove repository-scoped session records without starting the control plane:

```bash
lai sessions
lai sessions show <session-id>
lai sessions delete <session-id>
```

Session deletion removes only the current repository's matching persistent session record. It does not delete runs, metrics, audit events, source files, workspaces, Git branches, or remote resources.


Session state lives under `$LAI_DATA_DIR/control-sessions` as schema-versioned JSON, outside the repository. The directory is restricted to mode `0700`; session files are atomically replaced and restricted to `0600`. Each file is bound to the canonical repository root, so a session from another checkout is treated as unavailable rather than injected across projects. At most 100 session files are retained, each session keeps at most 12 turns, stored tasks are capped at 1200 characters, stored assistant text at 1800 characters, and prior context injected into a later run is capped at 6000 characters.

Historical session text is explicitly **untrusted context**. It may be stale, contain model mistakes, or include hostile instructions. The harness labels it accordingly and states that it cannot override the current request, `AGENTS.md`, active specs, policy, safety guards, or current repository evidence. A session-bound run does not become terminal-successful until its compact turn has been persisted; persistence failure is surfaced as a failed run instead of silently losing continuity.

The harness does not automatically copy environment variables, bearer tokens, model API keys, or full tool traces into the session record. User-provided task/output text can still contain sensitive information, so gateways should never send credentials as conversation text and operators should treat `$LAI_DATA_DIR/control-sessions` as private local state.

### Bounded delegate waves

`GET /v1/delegates/status` reports the delegate-wave fixture contract. `POST /v1/delegates/waves` accepts a bounded DAG of delegate tasks with explicit file ownership, dependencies, optional fixture outcome, max parallelism and parent-reserved delegate-slot budget. The current executor remains serial by default and fixture-only; it does not create subagents, copy tokens, copy approvals, learn policy, run unbounded swarms, or integrate changes automatically.

Each delegate record returns owned paths, changed-path metadata, dependency/validation status, budget accounting and authority flags. Raw stdout/stderr, workspace paths and secrets are not included. Cycles, unknown dependencies, ownership collisions, path escapes, copied authority material, exhausted delegate budget and unsupported parallelism fail before creating a successful wave. A failing dependency blocks dependent tasks; parent cancellation marks the tree cancelled. Integration remains only through the existing hash-bound promotion path.

`GET /v1/delegates/waves/<delegate_wave_id>` returns one sanitized wave record. `POST /v1/delegates/waves/<delegate_wave_id>/cancel` records cancellation intent across the wave tree; it does not kill arbitrary host processes or revoke unrelated sessions/runs.

### `GET /v1/mcp/status`

Returns the non-executing MCP broker status for repository-local config discovery. The payload reports loaded config files, declared servers, issues, and security flags. It does not start MCP servers, read environment variable values, or print credentials.

### `GET /v1/mcp/tools`

Returns declared MCP server summaries from the same broker discovery payload. It lists command names, argument counts, env key names, credential-shaped env keys, and blocked status for unsafe literal credential values. Tool execution remains disabled.


### `GET /v1/mcp/execution/status`

Returns the sandboxed fixture-MCP execution contract. It exposes the fixed `fixture_stdio` server identity, `write_artifact` tool schema, exact hashes required for execution, sandbox/readiness metadata and limits. It does not start a server or read repository MCP config as authority.

### `POST /v1/mcp/execution/call`

Executes exactly one `fixture_stdio` / `write_artifact` call after validating server, tool, config hash, tool-schema hash, path confinement under `artifacts/`, artifact size and sandbox readiness. The subprocess receives a minimal environment and runs through the verified sandbox executor. Public receipts contain outcome, reason code, hashes and bounded artifact metadata, not stdout/stderr bodies, absolute workspace paths, env values or secret material. Timeout after start returns terminal `outcome_unknown` with `retry_allowed=false`.

### `POST /v1/mcp/policy-check`

Classifies one MCP broker operation without execution. `status` and `list-tools` can be allowed as read-only non-executing operations. `call-tool` is denied in the MCP foundation milestone until allowlisted execution and audit boundaries are implemented.

### `POST /v1/policy-check`

Classifies one tool request through the same deterministic `ALLOW` / `ASK` / `DENY` policy used by the harness. It always returns `executed: false`.

## Scoped authority and approval intents

### `GET /v1/authority/presets`

Returns versioned Safe and work-sandbox authority presets. The effective authority rule is the intersection of preset, channel/backend controls and deterministic policy. In this v1 surface, both presets keep `shell_execution=false` and `mcp_tool_execution=false`; work-sandbox authority still means disposable workspace changes plus structured validation, not host shell or source-checkout mutation.

### `POST /v1/authority/intents`

Creates a durable approval intent only for policy `ASK` decisions. The intent is stored under `$LAI_DATA_DIR/control-approvals`, outside checkpoints and outside the repository, with a generated `ca-<16 hex>` ID, payload hash, destination, principal, TTL and repository/workspace/policy preconditions. The public response exposes only sanitized payload metadata such as tool, mode, backend, argument-key names and SHA-256 values; it does not echo raw tool arguments. Unsupported authority backends fail closed with `DENY` and `executed=false`.

### `POST /v1/authority/approvals`

Consumes exactly one matching approval intent by `approval_intent_id` and `payload_sha256`. Before marking it approved, the server checks use-once state, revocation, expiry, principal, repository/workspace/branch/Git-status preconditions and the current policy decision/reason. Replay, payload drift, another workspace, revoked intent, expiry or changed policy fail closed. This route records and consumes the approval but still returns `executed=false` and `execution_enabled=false`; it does not execute the tool payload.

### `DELETE /v1/authority/approvals/<approval_intent_id>`

Revokes one unused approval intent. Revocation does not delete audit, metrics, runs, sessions, source files, workspaces, branches, tags, releases, model files or remote resources.

## Credential broker foundation

### `GET /v1/credentials/status`

Returns the implemented fake credential-broker foundation. It reports `real_credentials_enabled=false`, supported adapter `fake`, TTL limits, and executor-environment constraints: no generic secret env injection, no argv secret injection, and opaque references only.

### `POST /v1/credentials/refs`

Creates an opaque `sr-<16 hex>` reference for the fake adapter with audience, operation, principal and TTL. The raw secret is stored only in the local data directory for the fake fixture and is not echoed to the client, model prompt, argv, generic environment, audit, metrics, run events or public status surfaces. Unsupported adapters return `DENY` with `executed=false`.

### `POST /v1/credentials/use`

Uses one active fake reference through the supervisor-controlled fake adapter after checking reference ID, adapter, audience, operation, expiry and revocation state. A successful fake delivery writes a private fake-recipient fixture and returns a sanitized receipt. If the request simulates timeout after send, the receipt reports `outcome_unknown` rather than pretending exactly-once delivery.

### `DELETE /v1/credentials/refs/<secret_ref>`

Revokes one credential reference. Revocation blocks future uses but does not delete already-written private fake-recipient fixture files or receipts.

## Governed egress

### `GET /v1/egress/status`

Returns the versioned egress policy surface without opening a connection: default-deny destination classes, implicit public evidence kinds, proxy environment names that are scrubbed, and sandbox bypass controls. Public `web_search` / `web_fetch` retain their lightweight read-only evidence behavior and include egress receipts. Registry and local-service exits require explicit broker grants; LAN, loopback, metadata, model backend, control API, browser automation, authenticated external actions, and ungranted registries/services are denied by default. Allowed domains are not treated as content trust.

## Authenticated external actions foundation

### `GET /v1/external-actions/status`

Returns the implemented fake external-action adapter surface. It reports adapter `fake_git_remote`, operation `push_branch`, credential-broker requirement, hash-bound intent requirement, protected-branch blocking, and `real_external_accounts_enabled=false`. Reading status does not touch remotes, accounts, GitHub, or the network.

### `POST /v1/external-actions/intents`

Creates one `ea-<16 hex>` intent for a fake Git remote branch effect. The request is bound to adapter, operation, principal, opaque `secret_ref`, credential audience/operation, target remote, target branch, source branch, source baseline SHA, patch SHA-256, optional expected remote SHA, and TTL. The server revalidates the current source branch and baseline before persisting the intent. Protected target branches are rejected. Unsupported adapters or operations return `DENY` with `executed=false`.

### `POST /v1/external-actions/execute`

Consumes one pending external-action intent by exact `external_action_id`, `payload_sha256`, and principal. Before the fake effect, it rechecks expiry, replay state, branch/baseline drift, protected branch policy, fake-remote expected SHA, and the credential reference through the broker. Success writes only the local fake-remote fixture and returns a sanitized `er-<16 hex>` receipt. If delivery is simulated as lost after send, the receipt reports `outcome_unknown` and `retry_allowed=false`; the action is still marked used and cannot be replayed automatically.

This foundation does not push to GitHub, create pull requests, merge, tag, publish releases, expose real account credentials, or give shell commands remote-Git authority. Real external accounts require a later additive contract and separate tests.

## Isolated fixture browser workflows

### `GET /v1/browser/status`

Returns the browser-workflow surface without starting a personal browser. The implemented adapter is `fixture_browser`: local `fixture://` pages only, disposable profile directory, no real browser engine, no JavaScript execution, no authenticated session, no personal profile and no public network egress.

### `POST /v1/browser/sessions`

Creates one `br-<16 hex>` fixture-browser session from a bounded HTML fixture and `fixture://` URL. The profile path is local and private; public responses include only session ID, URL, origin, DOM hash, status and expiry metadata. Fixture destinations named like control/model/metadata/localhost are blocked.

### `POST /v1/browser/sessions/<browser_session_id>/navigate`

Updates the fixture page to another bounded `fixture://` URL and HTML body. Navigation recomputes the DOM SHA-256 and records no browser cookies, credentials or external network state.

### `GET /v1/browser/sessions/<browser_session_id>/extract`

Returns bounded text extracted from the current fixture HTML. Script/style/noscript/SVG and tags are removed, secret-shaped strings are redacted, and the result is marked as untrusted browser content. Extracted page text is never approval authority.

### `GET /v1/browser/sessions/<browser_session_id>/screenshot`

Returns a bounded sanitized text-snapshot receipt with byte count and SHA-256, not a raw screen capture of a personal desktop. The preview is redacted and size-limited.

### `POST /v1/browser/sessions/<browser_session_id>/downloads`

Quarantines a bounded text/HTML/JSON fixture download under the LAI data directory and returns only filename, content type, size, SHA-256 and quarantine status. The quarantine path is not exposed publicly.

### `POST /v1/browser/sessions/<browser_session_id>/actions`

Records non-critical fixture actions and blocks critical actions unless an explicit external-action adapter is supplied. It requires the caller to provide the expected DOM SHA-256 and fails closed on DOM drift. The browser route itself never executes the external action adapter, never submits credentials and never performs a real purchase, send, merge, push or publication.

### `DELETE /v1/browser/sessions/<browser_session_id>`

Closes one fixture-browser session and removes its disposable profile directory. Existing quarantined download records and receipts remain local evidence.

## Asynchronous control runs

### `POST /v1/runs`

Accepts `mode` and `task`, plus an optional persistent `session_id`:

```json
{
  "mode": "plan",
  "task": "continue the previous architecture discussion",
  "session_id": "cs-0123456789abcdef"
}
```

Without `session_id`, the run remains one-shot and follows the existing behavior. With `session_id`, the session must already exist for the current repository; unknown or cross-repository IDs are rejected before child-process spawn.

Allowed run modes:

- read-only: `plan`, `review`, `security`, `diagnose`, `release`;
- work: `implement`, `fix`, `refactor`, `ci-fix`.

The task must be non-empty and at most 4000 characters. Unknown fields other than the optional `session_id` are rejected. The client cannot supply an executable, shell command, cwd, argv prefix, environment override, validation command, container image, or Docker options.

Accepted work returns `202` with a generated `control_run_id`. One worker serializes model use and at most four additional requests may wait in the queue. A full queue returns `429`.

Control-run children use fixed argv, `shell=False`, disabled stdin, a dedicated process group, and no client-supplied executable/cwd/env/container override. Read-only children still run with reduced tools. Work children are wrapped by the verified Docker sandbox profile before inference; missing enforcement blocks the run instead of falling back to host execution. They never auto-start the model service: if llama.cpp is offline, the run fails cleanly and service startup remains an explicit operations responsibility.

### Read-only runs

Read-only runs execute against the source checkout with capability-reduced inspection tools. They cannot receive write tools or `bash`. `plan`, `review`, `security`, and `diagnose` may additionally receive `web_search` / `web_fetch`, which are restricted to bounded governed public HTTPS evidence under the SSRF/redirect/egress rules in [Web evidence](WEB-EVIDENCE.md). `release` deliberately does not receive model-directed web tools.

### Work runs

Before spawning a work child, the control plane verifies the configured digest-pinned Docker image is locally available with `--pull=never`, then creates a unique safe workspace under the configured safe-workspace base. Only tracked source-repository contents are copied, the workspace gets its own isolated Git branch, and the child process is dispatched through the sandbox with that workspace mounted at `/workspace`.

Remote work profiles expose repository-confined read/write tools, `validate`, and bounded `sandbox_exec`; generic `bash` and direct source-checkout Git tools are absent. `sandbox_exec` runs only after the child proves the verified sandbox context, uses a minimal environment, blocks Git remote operations, host/system paths, Docker socket access, host dependency installation, and external registry/network use, but permits local workspace commands including offline fixture installs and local Git commits. The sandbox wrapper uses no network, no Docker socket, no host home, no host runtime/dependency-cache mounts, dropped capabilities, `no-new-privileges`, non-root user, read-only root filesystem, bounded CPU/memory/PIDs/tmpfs, and no host fallback. Existing path confinement, symlink rejection, stale-write protection, `AGENTS.md` handling, spec requirements, patch sanity, validation guards, and mode-specific progress guards continue to apply inside the isolated workspace.

When the child terminates, the control plane records a bounded workspace Git status, changed-path list, and diff. For safe workspaces, this evidence is computed against the seed commit so committed local sandbox changes remain reviewable and promotable. The source checkout is not modified.

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
- no host runtime, dependency-cache, host home, or secret-file mounts.

The harness never pulls a sandbox image automatically. If Docker or the configured local digest-pinned sandbox image is unavailable, a work run is rejected before model execution.

### `GET /v1/runs/<control_run_id>`

Returns `queued`, `running`, `succeeded`, `failed`, or `cancelled` plus timestamps, exit code, bounded stdout/stderr, truncation flags, and the tool-profile name.

For work runs it additionally returns the isolated workspace path, bounded Git status, changed paths, bounded diff, and a diff-truncation flag. Session-bound runs also return `session_id`, the number of prior turns used, historical-context character count, and whether the terminal turn was persisted. One-shot runs still do not create a control-plane transcript; session-bound runs persist only the bounded compact turn described above.

### `GET /v1/runs/<control_run_id>/events`

Returns a bounded metadata-only timeline derived from the control-run record: `queued`, `started`, optional `workspace_prepared`, optional `cancel_requested`, and terminal `finished` events. It also returns a versioned `trajectory` projection with sequence numbers, event/action/span IDs, reason codes, and allowlisted metadata for queueing, preflight, process lifecycle, output capture, workspace result collection, cancellation, persistence, and completion. It is intended for polling clients that need progress without reading run output.

The response does not include task text, stdout, stderr, transcripts, control tokens, model keys, raw diffs, workspace paths, or file contents. This route is read-only and authenticated like other run endpoints. It is not a streaming API; clients should poll it until `terminal` is true.

### `DELETE /v1/runs/<control_run_id>`

Cancels only that queued/running control run. A queued run is cancelled before spawn; a running child is terminated and escalated to kill after a short grace period if needed. The route does not delete Git refs, source files, historical run records, metrics, or audit evidence.

## Explicitly not exposed

The control plane still has no HTTP capability for:

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
                                                        |-> persistent session -> read-only/work run
                                                        |                    `-> bounded untrusted turn context
                                                        `-> isolated work workspace -> sandbox validate -> patch hash
                                                                                         -> approved promotion -> feature worktree
```

`lai-gateway` is intentionally a separate project. Messaging credentials, transport/user mapping, notification delivery, and commercial/social automation do not belong in the harness core. The harness stores only repository-scoped coding-session continuity behind its loopback bearer boundary.


## Session fork experiments

`GET /v1/experiments/status` reports the A9 fork/comparison surface. `POST /v1/experiments/forks` creates 2-4 child sessions from one parent session and the current Git base snapshot. Child sessions start empty; parent history is represented by a snapshot hash and remains untrusted historical context. Tokens, API keys, approval intents, process IDs and workspace paths are rejected rather than copied.

`GET /v1/experiments/{experiment_id}` returns the sanitized experiment record. `POST /v1/experiments/{experiment_id}/compare` compares completed run IDs assigned to forks. The comparison checks common base, validation status and patch hash before aggregate cost metadata. Different valid patches or failed validation produce `inconclusive`, not an automatic winner. Expired experiments fail closed. Integration remains only through the existing reviewed hash-bound promotion path.
