# Spec: Self-correcting development harness

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Close the repository development feedback loop with deterministic runtime hooks and make Harness Score L4 a CI-enforced invariant without weakening lai harness safety boundaries.

## Requirements

### REQ-001

Expose a deterministic, model-free `lai policy-check` interface that classifies a tool request through the existing `evaluate_tool_policy` boundary without executing the requested action.

### REQ-002

Add a repository-local shell gate hook that reuses `lai policy-check`, maps ALLOW/ASK/DENY to hook permissions, and fails closed on malformed or unavailable policy evidence.

### REQ-003

Add a repository-local feedback hook that performs fast, best-effort syntax/lint/format feedback only for edited files confined to the repository and never installs dependencies.

### REQ-004

Strengthen core shell policy so force-push, hard reset, npm publish, and destructive recursive PowerShell removal are DENY while ordinary Git mutation remains ASK.

### REQ-005

Add a dedicated read-only GitHub Actions workflow that gates repository maturity at Harness Score L4 using a pinned Harness Score action revision.

### REQ-006

Add focused automated coverage for policy-check and hook allow/ask/deny/fail-closed behavior, then prove the repository reaches L4 with Harness Score 1.6.3.

## Acceptance Criteria

- `lai policy-check` returns deterministic policy evidence and performs no requested tool action.
- The shell gate blocks known destructive actions, asks on sensitive Git mutation, and allows ordinary inspection commands.
- Malformed hook input cannot silently become allow.
- Feedback hook never escapes the repository and remains best-effort/non-blocking.
- Product CI and harness-maturity CI remain separate concerns.
- `npx --yes harness-score@1.6.3 . --min-level 4` exits successfully.

## Validation

- `REQ-001`: focused CLI/unit tests for `policy-check` plus install smoke.
- `REQ-002`: hook subprocess tests for allow, ask, deny, malformed input, and policy-check failure.
- `REQ-003`: hook tests for repository confinement and supported-file feedback behavior.
- `REQ-004`: existing policy classification/non-execution tests extended with destructive commands.
- `REQ-005`: YAML/static inspection plus Harness Score CI workflow validation.
- `REQ-006`: `make lint`, `make check`, `make test-dev`, `make test`, `make validate`, and `npx --yes harness-score@1.6.3 . --min-level 4`.

## Context and Constraints

The beta.8 repository measures L3 Sensing at 76/108 with Context 100%, Sensors 80%, and CI 100%. Harness Score explicitly reports L4 gaps of hooks >=70% and total >=80%. Existing pre-commit and product runtime policy should be reused instead of duplicated where practical.

## Non-Goals

- Do not add MCP configuration solely for score points.
- Do not add a fake subagent or delegation feature.
- Do not introduce a type checker until the extensionless monolithic Python runtime has a deliberate typing plan.
- Do not publish, tag, merge, or push as part of implementation validation.

## Implementation Notes

Prefer small Python hook scripts under `.cursor/hooks/` so they work with the repository's primary language and no runtime package dependencies. The shell gate should invoke the checked-in `src/local-agent --policy-check` path so a fresh clone does not depend on a prior install. Feedback remains advisory; CI is the final authority.

## Traceability

- `REQ-001` -> `src/local-agent`, `src/lai`, CLI tests, install smoke.
- `REQ-002` -> `.cursor/hooks.json`, `.cursor/hooks/guard_shell.py`, hook tests.
- `REQ-003` -> `.cursor/hooks/feedback_check.py`, hook tests.
- `REQ-004` -> policy patterns and regression tests.
- `REQ-005` -> `.github/workflows/harness-score.yml`.
- `REQ-006` -> focused/full validation and saved Harness Score before/after evidence.
