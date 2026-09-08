# Runtime records

LAI persists local workspace state, metrics, audit events, structured trajectory audit events, budget ledger audit events, durable approval-intent records, credential reference/receipt records, external-action fake remote intents/receipts, fixture-browser session/download records, sandbox-executor metadata, recovery checkpoints, pre-write snapshots, and repository-scoped remote-session records outside the repository. The formats are explicit, versioned contracts so persisted context never becomes implicit authority.

## Schema versions

New records use `schema_version: 1`.

Machine-readable contracts live in `schemas/runtime/`:

- `workspace_state.schema.json`
- `metric_event.schema.json`
- `audit_event.schema.json`
- `checkpoint.schema.json`
- `snapshot.schema.json`
- `control_session.schema.json`
- `gateway_contract.schema.json`

Trajectory audit events are embedded in `audit_event.schema.json` records with `type: trajectory`; budget ledger audit events use `type: budget` with a nested versioned reservation/consumption payload. The control-plane `/events` route exposes a separate in-memory trajectory projection for active/recent control runs.

The runtime remains Python-standard-library-only. JSON Schema documents are contracts and test fixtures; LAI does not install a JSON Schema validator at runtime.

Legacy unversioned workspace, metric, and audit records remain readable. Unsupported future metric/audit versions are ignored. Unsupported workspace/checkpoint/snapshot/control-session versions fail closed rather than being injected into current context, recovery, or rollback.

Pre-write snapshots live under `$LAI_DATA_DIR/snapshots`, are bound to one canonical repository root and run ID, and store bounded UTF-8 file contents only outside the repository so explicit rollback can verify current checkpoint hashes before restoring or deleting files.

Control sessions live under `$LAI_DATA_DIR/control-sessions`, are bound to one canonical repository root, retain at most 12 compact turns per session, and keep at most 100 session files. Approval intents live under `$LAI_DATA_DIR/control-approvals`, are versioned, use generated `ca-<16 hex>` IDs, and are bound to payload hash, principal, TTL, repository/workspace/branch/Git status and policy preconditions. Credential-broker fake refs and receipts live under `$LAI_DATA_DIR/credential-broker`; public broker surfaces expose opaque `sr-<16 hex>` refs, `rc-<16 hex>` receipts, hashes, audience, operation and outcome, not raw secret material. External-action fake Git remote intents and receipts live under `$LAI_DATA_DIR/external-actions`; public surfaces expose `ea-<16 hex>` intents, `er-<16 hex>` receipts, branch/ref/baseline hashes, payload hashes and terminal outcomes, not raw credentials. Fixture-browser sessions and quarantined downloads live under `$LAI_DATA_DIR/browser-workflows`; public surfaces expose `br-<16 hex>` sessions, DOM hashes, redacted text snapshots and download hashes, not profile paths or raw secret-like values. Sandbox-executor metadata is exposed as a sanitized capability/status record, not a raw Docker command or secret-bearing environment dump. Safe-workspace changed-path and patch evidence is derived from the seed commit to the current workspace tree, so committed local sandbox changes remain visible without treating workspace history as source authority. Local-chat workspace IDs are deterministic opaque projections of the served repository root, local-chat event cursors are sequence numbers over the existing in-memory trajectory projection, local-chat review objects are sanitized projections over live control-run/promotion state, and local-chat promotion requests carry only an exact `patch_sha256`. `lai chat-bootstrap` reads these public control-plane projections but does not persist a separate bootstrap grant, install optional components, open a browser, or start another runtime. They are not persistent grants or replay authority. Historical text is advisory/untrusted and current repository evidence always wins.

## Retention

Retention is local and bounded. Defaults preserve the pre-beta.18 behavior:

| Setting | Default | Purpose |
| --- | ---: | --- |
| `state_retention_days` | 45 | Remove stale per-repository workspace handoff files |
| `metrics_max_bytes` | 5000000 | Prune metrics after this file size |
| `metrics_keep_lines` | 3000 | Tail kept when metrics are pruned |
| `audit_max_bytes` | 5000000 | Prune audit after this file size |
| `audit_keep_lines` | 4000 | Tail kept when audit is pruned |

All settings follow `CLI > LAI_* environment > TOML > defaults`. Invalid, boolean, zero, negative, or excessively large values fail during configuration loading.

JSONL pruning replaces the file atomically after retaining the configured tail. Retention never deletes repository files, safe workspaces, promoted worktrees, Git history, release artifacts, or model files.

Workspace state is non-authoritative context: current repository evidence and the current request always override it. Audit/metrics retention therefore limits historical evidence but never changes runtime authority.
