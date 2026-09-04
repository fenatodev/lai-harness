# Spec: Spec-Driven Workflow

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Make lai harness use explicit specs to define requested changes before implementation, with stable requirement IDs and traceable validation.

## Requirements

### REQ-001

lai harness must recognize specs stored under `.specs/`.

### REQ-002

Requirements must use stable `REQ-NNN` identifiers.

### REQ-003

Each spec must declare `quick` or `full` workflow mode.

### REQ-004

Validation must reference the requirement IDs it verifies.


### REQ-005

Exactly one spec may have `Status: active`.

### REQ-006

The active spec must be injected as normative agent context.

### REQ-007

The active spec mode must select `quick` or `full` workflow guidance.
## Acceptance Criteria

- Active specs are discovered only under `.specs/`.
- Duplicate active specs fail closed.
- Invalid modes or requirement IDs fail closed.
- `--spec-status` reports active spec metadata without a model call.
- Agent context includes the active spec and mode guidance.

## Validation

- `REQ-001`, `REQ-005`: active-spec discovery tests.
- `REQ-002`, `REQ-003`: parser validation tests.
- `REQ-004`: traceability validation test.
- `REQ-006`, `REQ-007`: context injection tests.

## Context and Constraints

Specs are repository-local and must remain subordinate to `AGENTS.md` and repository safety rules. No workspace trust or policy-engine work belongs in alpha.7.

## Non-Goals

- Hooks, sandboxing, MCP routing, delegates, or learning.
- Automatic creation of specs by the model.

## Implementation Notes

Prefer deterministic parsing with no new runtime dependency. Draft specs must not affect runtime behavior.

## Traceability

- `REQ-001` -> active-spec discovery tests
- `REQ-002` -> requirement-ID parser tests
- `REQ-003` -> workflow-mode parser tests
- `REQ-004` -> validation-reference tests
- `REQ-005` -> duplicate-active-spec test
- `REQ-006` -> prompt-context test
- `REQ-007` -> quick/full guidance tests
