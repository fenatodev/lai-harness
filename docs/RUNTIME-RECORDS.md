# Runtime records

LAI persists local workspace state, metrics, audit events, recovery checkpoints, pre-write snapshots, and repository-scoped remote-session records outside the repository. The formats are explicit, versioned contracts so persisted context never becomes implicit authority.

## Schema versions

New records use `schema_version: 1`.

Machine-readable contracts live in `schemas/runtime/`:

- `workspace_state.schema.json`
- `metric_event.schema.json`
- `audit_event.schema.json`
- `checkpoint.schema.json`
- `snapshot.schema.json`
- `control_session.schema.json`

The runtime remains Python-standard-library-only. JSON Schema documents are contracts and test fixtures; LAI does not install a JSON Schema validator at runtime.

Legacy unversioned workspace, metric, and audit records remain readable. Unsupported future metric/audit versions are ignored. Unsupported workspace/checkpoint/snapshot/control-session versions fail closed rather than being injected into current context, recovery, or rollback.

Pre-write snapshots live under `$LAI_DATA_DIR/snapshots`, are bound to one canonical repository root and run ID, and store bounded UTF-8 file contents only outside the repository so explicit rollback can verify current checkpoint hashes before restoring or deleting files.

Control sessions live under `$LAI_DATA_DIR/control-sessions`, are bound to one canonical repository root, retain at most 12 compact turns per session, and keep at most 100 session files. Their historical text is advisory/untrusted and current repository evidence always wins.

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
