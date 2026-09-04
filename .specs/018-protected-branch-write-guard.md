# Spec: Protected branch write guard

## Metadata

- Mode: `full`
- Status: `done`

## Goal

Prevent accidental model-generated repository edits on published or release-sensitive branches.

## Requirements

### REQ-001

Write-capable repository tools must be denied on `main`, `master`, and `release/*` by default.

### REQ-002

Read-only modes and read-only deterministic commands must remain usable on protected branches.

### REQ-003

A deliberate local override must exist for exceptional maintenance, and the denial reason must tell the operator how to use a branch instead.

## Acceptance Criteria

- Policy denies `patch`, `edit`, `create`, and `rewrite` on protected branches.
- Policy still allows write tools on feature/test branches.
- `LAI_ALLOW_PROTECTED_BRANCH_WRITES=1` overrides the branch guard.
- Release/readiness checks remain read-only and deterministic.

## Validation

- `REQ-001`: policy regression test for `main` and `release/*`.
- `REQ-002`: focused readiness/release-check tests.
- `REQ-003`: override regression test.

## Context and Constraints

The guard is a safety backstop after local smoke testing showed that `lai implement` can correctly modify files while a user is still thinking in release context.

## Non-Goals

- No automatic branch creation.
- No tag, merge, push, upload, or publication automation.
- No claim that protected branches are a sandbox.

## Implementation Notes

Keep the policy deterministic and independent of model calls. The check belongs in `evaluate_tool_policy` before executing write tools.

## Traceability

- `REQ-001`: `evaluate_tool_policy`, `is_protected_write_branch`.
- `REQ-002`: read-only modes and release-check behavior.
- `REQ-003`: `LAI_ALLOW_PROTECTED_BRANCH_WRITES`.
