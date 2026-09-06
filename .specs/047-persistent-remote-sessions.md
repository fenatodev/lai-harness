# Spec: persistent remote sessions

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Allow authenticated control-plane clients to continue multiple bounded runs under one persistent session without granting new shell, Git, model-management, or source-checkout authority.

## Requirements

### REQ-001

Add a typed, standard-library-only `src/lai_sessions.py` module for versioned, atomic, bounded session persistence under the LAI data directory.

### REQ-002

Expose authenticated create/list/get session endpoints and advertise persistent-session capability in `/v1/status`.

### REQ-003

Allow `POST /v1/runs` to accept an optional `session_id`; reject unknown/missing sessions before model execution and include session metadata in sanitized run records.

### REQ-004

For session-bound runs, prepend only bounded prior turn context, clearly labeled as untrusted historical context that cannot override the current request, repository rules, policy, specs, or current file evidence.

### REQ-005

Persist each terminal session-bound turn with bounded task/output evidence so a later control-server process can continue the same session. Persistence failure must be visible and must not be reported as a successful persistent turn.

### REQ-006

Install the new module, add a versioned runtime schema, semantic navigation, and strict-mypy ratchet coverage without adding runtime dependencies.

### REQ-007

Update control-plane documentation and roadmap state while preserving all existing remote shell-free/workspace/promotion boundaries.

## Acceptance Criteria

- Sessions survive control-server restart because canonical state lives on disk, not only in server memory.
- Session files are repository-external, atomic, mode-restricted, bounded to recent turns, and reject unsafe IDs/symlinks/future schema versions.
- Session-bound second runs receive prior compact context; ordinary runs remain behaviorally unchanged.
- Unknown `session_id` fails before child process spawn.
- No endpoint gains generic shell, arbitrary argv/env/cwd, direct source checkout write, commit/push/merge/tag/release, model switching, or dependency installation.

## Validation

- `REQ-001`: direct unit tests for create/load/list/append/context bounds and persistence safety.
- `REQ-002`: control-plane endpoint tests for create/list/get and capability reporting.
- `REQ-003`: run submission tests for valid/unknown session IDs and sanitized metadata.
- `REQ-004`: fake-child assertion that second session run argv contains bounded untrusted history plus the current request.
- `REQ-005`: restart/load test and persistence-failure regression.
- `REQ-006`: install smoke, runtime-schema test, semantic contract test, and `make typecheck`.
- `REQ-007`: focused control-plane/security regressions plus final milestone gate when the post-v0.4.0 batch is frozen.

## Context and Constraints

Current control runs are one-shot subprocesses. The server keeps queue/run lifecycle state in memory and historical metrics/audit records separately, but no caller-scoped conversation identity or compact multi-turn context exists. The gateway must remain separate from the harness.

## Non-Goals

- Do not implement Telegram, PWA, Tailscale, notifications, browser actions, web search, MCP, or gateway credentials.
- Do not add multi-user authentication or share sessions across repositories.
- Do not automatically capture environment variables, control/model API tokens, full tool traces, or unlimited transcripts. User-provided session text may itself be sensitive and must remain local with restrictive permissions; gateways must not send credentials as conversation text.
- Do not change the default model or expose model lifecycle controls.

## Implementation Notes

Use individual JSON files under `$LAI_DATA_DIR/control-sessions`, schema version 1, restrictive permissions, atomic replacement, bounded turn count, and bounded text fields. Keep session history advisory/untrusted. Let the existing globally serialized control worker naturally order turns.

## Traceability

- `REQ-001` -> `src/lai_sessions.py`, direct session tests.
- `REQ-002` -> `src/local-agent`, control-plane endpoint tests.
- `REQ-003` -> `control_submit_run`, public run record regressions.
- `REQ-004` -> worker task composition regression.
- `REQ-005` -> session append/reload/failure regressions.
- `REQ-006` -> installer, runtime schema, semantic contract, mypy/quality sensors.
- `REQ-007` -> `docs/CONTROL-PLANE.md`, `ROADMAP.md`, control-plane security tests.

## Validation Evidence

- Added typed stdlib-only `src/lai_sessions.py` with atomic `0600` files under a `0700` session directory, repository binding, 100-session retention, 12-turn retention, bounded task/assistant fields, and 6000-character historical-context budget.
- Added authenticated create/list/get session endpoints plus optional `session_id` on `POST /v1/runs`; unknown/cross-repository sessions fail before subprocess spawn.
- Session history is injected with an explicit untrusted/stale warning and never changes the existing policy/tool profile. Terminal success is not published until the compact turn persists; persistence failure returns a failed run.
- Added runtime schema `control_session.schema.json`, semantic subsystem `remote-sessions`, standalone installer support, and strict mypy coverage; ratchet increased from 5 to 6 files.
- Focused session/control regressions passed, including cross-repository isolation, server re-open, context reuse, unknown-session pre-spawn rejection, and persistence failure.
- Broad focused regression set: 42 passed + 7 subtests.
- Full `make milestone-gate`: 262 pytest + 86 subtests; 262 unittest; strict mypy over 6 files; Harness Score L4 100/108 (93%); publication scan and VSIX inspection green; exit 0.
- Runtime/extension version remains `0.4.0`; no push, PR, tag, GitHub Release, model switch, dependency install, or remote-authority expansion occurred.
