# LAI Harness Specs

Specs define WHAT must change before implementation begins.

## File naming

Use:

`NNN-short-description.md`

Example:

`001-spec-driven-workflow.md`

## Requirement IDs

Every behavioral requirement must have a stable ID:

- `REQ-001`
- `REQ-002`
- `REQ-003`

Requirement IDs must remain stable while the spec exists.

## Workflow modes

Each spec declares one workflow mode:

- `quick` for small, low-risk changes.
- `full` for broader or higher-risk changes.

## Status

- `draft` is ignored by runtime.
- `active` is normative for the current change.
- `complete` is retained for traceability and ignored by runtime.

At most one numbered spec may be `active`. Multiple active specs fail closed.

### quick

Requires:

- goal;
- requirements;
- acceptance criteria;
- validation.

### full

Use for:

- multiple subsystems;
- public interfaces;
- architecture changes;
- security-sensitive changes;
- release-critical behavior.

## Required sections

Every spec must contain:

1. Metadata
2. Goal
3. Requirements
4. Acceptance Criteria
5. Validation

Full specs also contain:

6. Context and Constraints
7. Non-Goals
8. Implementation Notes
9. Traceability

## Principle

Specs define the requested change.

They must not override:

- `AGENTS.md`;
- `.agents/rules/`;
- safety or release policy.
