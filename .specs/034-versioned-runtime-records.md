# Spec: Versioned runtime records and retention

## Metadata
- Mode: `full`
- Status: `complete`

## Goal
Make persisted LAI state, metrics, audit events, and recovery records explicitly versioned and retention-aware before persistent remote sessions depend on them.

## Requirements
### REQ-001
New workspace-state, metric-event, and audit-event records declare `schema_version: 1`; recovery checkpoints remain explicitly versioned.

### REQ-002
Publish machine-readable JSON Schema documents for workspace state, metric events, audit events, and recovery checkpoints without adding a runtime dependency.

### REQ-003
Readers remain backward-compatible with unversioned legacy metric/audit/workspace records and ignore or reject unsupported future schema versions safely.

### REQ-004
State, metrics, and audit retention limits are configurable through the existing CLI/environment/TOML precedence and validated as bounded positive integers.

### REQ-005
JSONL pruning is deterministic and atomic, preserving only the configured tail once the configured byte threshold is exceeded.

### REQ-006
Runtime authority, model behavior, remote capability profiles, promotion boundaries, and release authority remain unchanged.

## Acceptance Criteria
- `workspace_state.schema.json`, `metric_event.schema.json`, `audit_event.schema.json`, and `checkpoint.schema.json` parse as JSON and declare draft 2020-12.
- New metric/audit/workspace records contain `schema_version = 1`.
- Legacy unversioned records still appear in run history and workspace handoff.
- Future unsupported metric/audit records are skipped; unsupported workspace/checkpoint state fails closed.
- Defaults preserve the current operational posture: state 45 days, metric/audit files 5 MB, metric tail 3000 lines, audit tail 4000 lines.
- Invalid retention values fail closed during configuration loading.
- Focused record/retention regressions plus the full publication gate are green.

## Validation
- `REQ-001/002/003`: focused runtime-record schema tests.
- `REQ-004/005`: configuration and deterministic pruning tests.
- `REQ-006`: full regression, policy, control-plane, promotion, release, and publication gates.

## Context and Constraints
Retention settings govern local observability files only. They must not delete repository files, safe workspaces, promoted worktrees, or Git history.

Legacy records exist on developer machines, so migration is read-compatible rather than destructive. JSON Schema files are documentation/contracts and test fixtures; runtime validation stays standard-library-only.

## Non-Goals
- No persistent remote session implementation yet.
- No database migration or SQLite dependency.
- No MCP, browser, web-search, subagent, commit/push/PR authority, or new runtime dependency.

## Traceability
- `REQ-001/003` -> `src/local-agent`, runtime-record regressions.
- `REQ-002` -> `schemas/runtime/*.schema.json`, schema regressions.
- `REQ-004/005` -> configuration parser, JSONL retention helper, configuration/retention regressions.
- `REQ-006` -> existing full validation and release gates.

## Validation Evidence
- Focused runtime-record/config/state/checkpoint regressions: 12 passed.
- Full pytest: 217 passed + 72 subtests.
- Full unittest: 217 passed.
- Ruff, strict mypy, compile/static checks, `git diff --check`: green.
- Harness maturity no-regression gate: L4, 100/108.
- Publication scan and VSIX inspection: green.
