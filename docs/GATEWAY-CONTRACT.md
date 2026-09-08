# Gateway contract

For architecture context, see [Architecture](ARCHITECTURE.md), [Diagrams](DIAGRAMS.md), and [CLI reference](CLI-REFERENCE.md).


`lai gateway-contract --json` and authenticated `GET /v1/gateway-contract` expose a stable machine-readable contract for companion gateways such as `lai-gateway`.

The contract lets the separate Gateway discover the harness boundary without scraping prose or coupling to an exact patch release. Current private web/mobile access and future local web chat use the same ownership boundary: Gateway handles the user interface and client authentication; the harness owns execution, policy, workspace effects, and promotion. Messaging credentials and transport/user mapping stay with the Gateway.

This document describes the implemented v1 contract. The [target architecture](TARGET-ARCHITECTURE.md) plans Gateway as the primary local web chat and harness as the sole execution authority. The v1 contract now exposes scoped authority presets, durable approval intents, and an additive local-chat/inspector channel for read-only chat, bounded local inspection, sandboxed work-run review, and exact hash-bound promotion. Full / Trusted, remote approval UX and approved tool-payload execution remain unavailable.

## Local CLI

```bash
lai gateway-contract --json
```

The local CLI command is deterministic and does not call the model server. It includes product/version, schema version, supported control-plane routes, run modes, request/session/run limits, companion expectations, and explicit forbidden capabilities. `lai chat-bootstrap --json` is the separate Linux/WSL diagnostic that checks an already-running loopback control endpoint, local-chat negotiation, registered workspace/model, sandbox readiness, and first Safe chat availability. `lai distribution status --json` reports installed-state, explicit upgrade/rollback/uninstall policy and publication non-effects without contacting the model server. `lai validation matrix --json` reports the risk-proportional validation inventory without running checks or changing required-check settings.

## HTTP endpoint

```http
GET /v1/gateway-contract
Authorization: Bearer <control-api-token>
```

The endpoint is served by `lai serve` and uses the same bearer-authenticated JSON boundary as the rest of the control plane. It is still loopback-only; a private gateway may proxy it, but the harness does not bind to LAN, tailnet, or public addresses.

## Distribution diagnostics

The harness exposes distribution readiness through the local CLI, not a remote browser-facing API:

```bash
lai distribution status --json
```

The payload is schema-versioned and reports whether `$LAI_DATA_DIR/distribution/installed-state.json` was detected, the installed and previous versions, local artifact backup availability, uninstall preservation policy, one-model-runtime policy and explicit non-effects for release/tag/push/VSIX publication/model download/autoupdate. Unknown future state schemas fail closed locally and preserve data. Gateways may display these fields as operator diagnostics, but they do not grant upgrade, rollback, publication or host-install authority.

## Validation matrix diagnostics

The local validation matrix exposes retained check IDs, risk profiles, cost tiers, failure fixtures, Python-floor rationale and duplication comparison. It is metadata-only: `executed_checks=false`, `weakens_existing_gates=false` and `remote_settings_mutated=false`. Gateways may display it as guidance for which local evidence is expected for a risk class, but they must not treat it as proof that a check ran. Required checks, branch protections and publication gates remain explicit local command results or external CI evidence.

## Local chat / inspector channel

The additive local-chat channel is negotiated separately with:

```http
GET /v1/local-chat/contract?client_version=1
GET /v1/local-chat/workspaces?client_version=1
GET /v1/local-chat/models?client_version=1&workspace_id={workspace_id}
GET /v1/local-chat/content?client_version=1&workspace_id={workspace_id}&path={relative_path}
POST /v1/local-chat/runs
GET /v1/local-chat/runs/{control_run_id}/events?client_version=1&cursor=N
GET /v1/local-chat/runs/{control_run_id}/review?client_version=1&workspace_id={workspace_id}
POST /v1/local-chat/runs/{control_run_id}/promotion
POST /v1/local-chat/runs/{control_run_id}/lifecycle
```

Local-chat POST requests require bearer auth, loopback `Host`, loopback `Origin` when present, and the negotiated `X-LAI-CSRF` value. Workspace selection uses server-generated `lw-<16 hex>` IDs; client-supplied paths and model IDs are labels to validate, not authority. Model choices are manually selected server-approved labels; router selection is disabled and session grants are preserved across manual model selection. This channel can enqueue read-only control runs, enqueue A3 verified-sandbox work runs, and poll metadata-only trajectory events by cursor. It can expose bounded sanitized UTF-8 file text for local inspector display, after repository confinement, symlink rejection, binary rejection, size limits and token/secret-pattern redaction.

Work review is a UI projection over harness state. It exposes mode/status/tool profile, lifecycle availability, changed paths, bounded redacted diff preview, validation state, budget projection metadata, ASK status, and a hash-bound promotion proposal. Promotion through local-chat requires one exact `patch_sha256` and reuses the existing harness promotion path; stale hashes fail and repeated approved hashes are idempotent. Lifecycle currently supports idempotent cancel; pause/continue are explicit non-capabilities.

The bootstrap journey for Linux/WSL is deterministic: `lai chat-bootstrap` reads the existing control token, contacts the operator-started `lai serve` loopback endpoint, negotiates the local-chat contract, selects the server-registered workspace and default model, reports Gateway/sandbox/model readiness, and attempts one Safe `plan` chat only when the model backend is already ready. It does not install Gateway, open a browser, start a second persistent runtime, or download a model.

The channel explicitly does not enable source-checkout writes, host shell, remote approval execution, generic MCP tool execution, personal/authenticated browser automation, direct llama proxying, arbitrary model path selection, automatic model routing, model download, or cloud fallback.

Mode skills may expose declarative contract metadata through readiness/status surfaces: schema version, skill version, provenance, required context, tools, capabilities, validation and expected outputs. Gateways must treat skill declarations as display/diagnostic data only. They do not create grants, execute hooks, install packages, change tool profiles, or override policy.

## Secret boundary

The payload must not include bearer tokens, model API keys, secret file contents, host environment variables, private run transcripts, or persistent-session turn bodies. Gateways must keep the control bearer token server-side and must not send it to browsers, chat clients, logs, or model prompts.

## Explicit non-authority

The contract does not grant generic host shell, direct source-checkout writes, host dependency installation, ungoverned external registry/network access, remote Git, push/merge/PR authority, tag/release publication, personal/authenticated browser automation, JavaScript execution, direct llama.cpp exposure, or token disclosure. Governed public web evidence remains evidence-only; registry/local-service exits require explicit grants.

Remote work remains source-checkout-free and generic-`bash`-free, in disposable workspaces, and requires the verified sandbox executor profile before inference. The work profile may expose bounded `sandbox_exec` inside that sandbox for local workspace commands, offline fixture installs, tests/processes, and local isolated Git commits. The sandbox image is digest-pinned, uses `--pull=never`, disables network and sensitive host mounts, and fails closed without host fallback. Current run-time `ASK` still terminates the run. The authority-intent routes can persist and consume a hash-bound approval record, but they deliberately return `executed=false` and do not resume or execute a suspended tool call. The polling run-event surface does not expose a full trajectory stream. Future capabilities require versioned additive contracts, explicit negotiation, authorization, and dedicated implementation specs; older clients must retain their existing authority ceiling.

Schema file: [`schemas/runtime/gateway_contract.schema.json`](../schemas/runtime/gateway_contract.schema.json).

## Authority foundation

The contract includes authority-discovery and approval-intent routes:

```http
GET /v1/authority/presets
POST /v1/authority/intents
POST /v1/authority/approvals
DELETE /v1/authority/approvals/{approval_intent_id}
```

Gateways may display these records as review material, but must not treat chat text, checkpoints, prior runs, browser UI state or model output as approval authority. Approval consumption is use-once and bound to principal, payload hash, repository/workspace/branch/Git status and current policy. A consumed approval does not execute a payload in v1.

## Credential broker foundation

The contract includes a fake credential-broker fixture, not real account access:

```http
GET /v1/credentials/status
POST /v1/credentials/refs
POST /v1/credentials/use
DELETE /v1/credentials/refs/{secret_ref}
```

References are opaque and bound to audience, operation and TTL. Public responses include hashes and receipts, not secret material. The fake adapter can produce `delivered` or `outcome_unknown` receipts. Real OAuth, vaults, financial operations, cloud administration and broad credential forwarding remain out of scope.

## Authenticated external actions foundation

The contract includes a fake Git remote adapter, not real GitHub or provider access:

```http
GET /v1/external-actions/status
POST /v1/external-actions/intents
POST /v1/external-actions/execute
```

A fake remote action is explicit, hash-bound, credential-brokered, branch-scoped, TTL-bound and use-once. Execution revalidates source branch, source baseline, target branch policy, expected fake-remote SHA and credential audience/operation. Public receipts expose `delivered` or `outcome_unknown` plus hashes and IDs, not secret material. `outcome_unknown` is terminal for that intent and must not be retried automatically. Real provider pushes, pull requests, protected merges, tags, releases and publication remain outside this contract.

## Isolated fixture browser workflows

The contract includes a local fixture browser adapter, not a personal browser or real authenticated account session:

```http
GET /v1/browser/status
POST /v1/browser/sessions
POST /v1/browser/sessions/{browser_session_id}/navigate
GET /v1/browser/sessions/{browser_session_id}/extract
GET /v1/browser/sessions/{browser_session_id}/screenshot
POST /v1/browser/sessions/{browser_session_id}/downloads
POST /v1/browser/sessions/{browser_session_id}/actions
DELETE /v1/browser/sessions/{browser_session_id}
```

The fixture adapter accepts bounded `fixture://` pages, creates a disposable local profile, exposes sanitized extraction and screenshot snapshots, quarantines bounded downloads and requires DOM-hash preconditions for actions. Critical actions are blocked unless represented by a separate explicit adapter; the browser route does not execute those adapters itself. JavaScript execution, public web navigation, personal browser profiles, real logins, purchases, sends and provider-side Git effects remain outside this contract.

## MCP broker foundation

The control plane exposes MCP broker diagnostics and one fixture execution contract for companion clients:

- `GET /v1/mcp/status` reports repository-local MCP config readiness.
- `GET /v1/mcp/tools` lists declared MCP server summaries without starting servers.
- `POST /v1/mcp/policy-check` classifies MCP status/list/call operations without execution.

Generic `call-tool` remains denied through policy-check. Credential-shaped env values must use `${ENV_VAR}` interpolation and literal values are blocked without being printed.

The additive fixture execution contract is:

```http
GET /v1/mcp/execution/status
POST /v1/mcp/execution/call
```

It supports only `fixture_stdio` / `write_artifact`, requires exact server-config and tool-schema hashes, runs under the verified sandbox executor with a minimal environment, writes bounded artifacts under `artifacts/` in a disposable MCP workspace, and returns sanitized receipts. Repository configuration and server annotations do not grant authority. Real private servers, HTTP MCP, OAuth, sampling/callbacks and wildcard tools require later specs; see [MCP broker](MCP-BROKER.md).

## Session lifecycle

The contract includes repository-scoped persistent-session lifecycle routes:

```http
POST /v1/sessions
GET /v1/sessions?limit=N
GET /v1/sessions/{session_id}
DELETE /v1/sessions/{session_id}
GET /v1/experiments/status
POST /v1/experiments/forks
GET /v1/experiments/{experiment_id}
POST /v1/experiments/{experiment_id}/compare
GET /v1/delegates/status
POST /v1/delegates/waves
GET /v1/delegates/waves/{delegate_wave_id}
POST /v1/delegates/waves/{delegate_wave_id}/cancel
```

Deletion removes only the matching session record for the currently served repository. It does not delete runs, metrics, audit logs, source files, workspaces, Git branches, tags, releases, model files, or remote resources.

Fork experiments create child sessions for comparison. Bounded delegate waves are a separate fixture-only contract for orchestrating a small DAG with explicit file ownership, parent-reserved delegate-slot budget, dependency handling and sanitized aggregation. They do not run unbounded swarms, copy grants/tokens/approvals/processes, learn policy, select winners or integrate code automatically. Experiment and delegate records expire and are stored as sanitized local runtime state.
