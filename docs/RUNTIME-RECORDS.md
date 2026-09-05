# Runtime records

LAI persists local workspace state, metrics, audit events, and recovery checkpoints outside the repository. Beta.18 makes those formats explicit contracts before persistent remote sessions depend on them.

## Schema versions

New records use `schema_version: 1`.

Machine-readable contracts live in `schemas/runtime/`:

- `workspace_state.schema.json`
- `metric_event.schema.json`
- `audit_event.schema.json`
- `checkpoint.schema.json`

The runtime remains Python-standard-library-only. JSON Schema documents are contracts and test fixtures; LAI does not install a JSON Schema validator at runtime.

Legacy unversioned workspace, metric, and audit records remain readable. Unsupported future metric/audit versions are ignored. Unsupported workspace/checkpoint versions fail closed rather than being injected into current context or recovery.

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
