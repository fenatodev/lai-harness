# Spec: Policy and Lifecycle

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Centralize tool authorization behind explicit `ALLOW`, `ASK`, and `DENY` decisions and make policy outcomes auditable without broadening runtime capabilities.

## Requirements

### REQ-001

Every builtin tool action must pass through one deterministic policy decision boundary.

### REQ-002

`ALLOW` actions may execute normally.

### REQ-003

`ASK` actions must not execute automatically and must report that explicit user action or approval is required.

### REQ-004

`DENY` actions must fail closed and must not execute.

### REQ-005

Mutating Git and dependency-install commands must be classified as `ASK`; destructive system, filesystem, Docker, and database commands must be `DENY`.

### REQ-006

Read-only Git inspection and ordinary non-sensitive shell validation must remain `ALLOW`.

### REQ-007

Every `ASK` or `DENY` decision must emit an audit event containing the tool, decision, and reason.

### REQ-008

Policy must never broaden mode tool allowlists, repository confinement, validation guards, or other existing safety gates.

## Acceptance Criteria

- A single policy evaluator returns only `ALLOW`, `ASK`, or `DENY`.
- Sensitive commands are blocked before subprocess execution.
- Existing safe shell and read-only Git behavior remains operational.
- Policy audit events are visible in the audit trail.
- Existing safety and validation tests remain green.

## Validation

- `REQ-001`, `REQ-002`: centralized evaluator and allow-path tests.
- `REQ-003`, `REQ-005`: ASK classification and no-execution tests.
- `REQ-004`, `REQ-005`: DENY classification and no-execution tests.
- `REQ-006`: safe shell/read-only Git regression tests.
- `REQ-007`: policy audit-event tests.
- `REQ-008`: mode and guard regression suite.

## Context and Constraints

Alpha.7 already provides spec-driven workflow. Current shell safety is split between a Git mutation parser, regex denylist, mode-specific tool schemas, and lifecycle guards. Alpha.8 centralizes authorization semantics but does not create OS containment.

## Non-Goals

- Sandbox, container executor, process isolation, or filesystem virtualization.
- Interactive approval UI or persistent user approval grants.
- MCP, plugin, network, delegation, or learning policy adapters.

## Implementation Notes

Keep the evaluator deterministic and dependency-free. `ASK` is a stop-and-escalate decision, not permission to execute. Existing mode and validation gates remain independent defense-in-depth layers.

## Traceability

- `REQ-001` -> centralized policy evaluator tests
- `REQ-002` -> ALLOW execution tests
- `REQ-003` -> ASK no-execution tests
- `REQ-004` -> DENY no-execution tests
- `REQ-005` -> command classification matrix tests
- `REQ-006` -> safe command regression tests
- `REQ-007` -> audit policy event tests
- `REQ-008` -> full guard regression suite
