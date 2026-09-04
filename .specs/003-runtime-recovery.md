# Spec: Runtime and Recovery

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Persist a minimal deterministic run checkpoint so interrupted work can be inspected and resumed explicitly only when repository state still matches the recorded execution boundary.

## Requirements

### REQ-001

Each non-selection run must maintain a workspace-scoped checkpoint outside the repository containing run identity, mode, task, lifecycle phase, repository branch, Git status, and tracked file hashes.

### REQ-002

Checkpoint writes must be atomic so interruption cannot leave a partially written recovery record.

### REQ-003

Lifecycle transitions must update the checkpoint at deterministic boundaries including run start, tool completion, validation state, user-action escalation, normal completion, and terminal failure.

### REQ-004

An incomplete prior checkpoint must be detectable without calling the model and must be inspectable through a deterministic `lai recovery` command.

### REQ-005

Recovery compatibility must fail closed when the current branch, relevant Git status, or any recorded tracked-file hash differs from the checkpoint.

### REQ-006

Recovery must be explicit. A resume action may restore task/context metadata but must never replay a previously recorded tool call or shell command automatically.

### REQ-007

A compatible explicit resume must start a new run identity, record that it was resumed from the prior run, and inject bounded recovery context beneath current repository rules and active spec context.

### REQ-008

Completed, user-action-required, denied, or otherwise terminal checkpoints must not be offered as resumable interrupted work.

### REQ-009

Recovery events and compatibility failures must be auditable without weakening existing policy, validation, repository-confinement, or Git-mutation controls.

## Acceptance Criteria

- Checkpoint JSON is stored outside the repository and replaced atomically.
- `lai recovery` reports `none`, `interrupted`, `blocked`, or terminal state without contacting the model.
- Branch/status/hash drift blocks resume with concrete reasons.
- `lai resume` requires an incomplete compatible checkpoint and creates a fresh run linked to the prior run ID.
- Resume never replays a recorded tool call; the model receives only bounded recovery metadata and current repository evidence.
- Existing policy, guard, validation, state, audit, and publication tests remain green.

## Validation

- `REQ-001`, `REQ-003`: checkpoint schema and lifecycle transition tests.
- `REQ-002`: atomic write replacement/failure tests.
- `REQ-004`: deterministic recovery-status CLI tests.
- `REQ-005`: branch, Git-status, and tracked-hash drift tests.
- `REQ-006`, `REQ-007`: explicit resume integration tests proving fresh run identity and no tool replay.
- `REQ-008`: terminal-state resumability tests.
- `REQ-009`: recovery audit tests plus full guard regression suite.

## Context and Constraints

Alpha.8 provides deterministic `ALLOW` / `ASK` / `DENY` policy and stop-and-escalate lifecycle behavior. Workspace state and handoff already persist coarse context, while model truncation has bounded retry. Alpha.9 adds run recovery without treating persisted state as authoritative over current repository evidence.

## Non-Goals

- Automatic continuation after process restart.
- Replaying prior tool calls, shell commands, edits, or approvals.
- OS sandboxing, containers, process isolation, or filesystem virtualization.
- Context-ranking or repository-intelligence work reserved for alpha.10.
- MCP, plugins, delegation, or learning.

## Implementation Notes

Use a small versioned checkpoint schema and standard-library-only atomic replacement. Store only bounded task/context metadata plus hashes needed to prove compatibility. Current repository rules, policy, active spec, and live Git evidence always override checkpoint content.

## Traceability

- `REQ-001` -> checkpoint schema/path tests
- `REQ-002` -> atomic checkpoint write tests
- `REQ-003` -> lifecycle checkpoint tests
- `REQ-004` -> recovery status CLI tests
- `REQ-005` -> compatibility drift tests
- `REQ-006` -> no-replay resume integration test
- `REQ-007` -> fresh-run recovery context tests
- `REQ-008` -> terminal checkpoint tests
- `REQ-009` -> recovery audit and full regression tests
