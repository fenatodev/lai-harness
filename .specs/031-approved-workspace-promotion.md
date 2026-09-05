# Spec: approved workspace promotion

## Metadata
- Mode: `full`
- Status: `complete`

## Goal
Promote a successful isolated remote-work result into a dedicated durable Git worktree/feature branch only after an exact patch hash is approved, while keeping the source checkout unchanged.

## Requirements
### REQ-001
Only terminal `succeeded` work runs with a non-empty isolated-workspace patch may produce a promotion proposal. Failed, cancelled, queued, running, read-only, empty, oversized, or unsafe-path results are not promotable.

### REQ-002
Capture source branch, source SHA, and source-clean state in safe-workspace metadata. Promotion requires a clean source baseline and revalidates that the current source checkout is still clean, on the same branch and SHA.

### REQ-003
Build the promotion patch from structured Git porcelain data and a complete bounded binary-capable patch. Compute SHA-256 over the exact patch bytes; the UI diff remains display evidence only.

### REQ-004
Expose `GET /v1/runs/<id>/promotion` as a read-only proposal endpoint containing promotable status/reasons, source baseline, changed paths, patch hash/size, and no secrets or arbitrary paths.

### REQ-005
Expose `POST /v1/runs/<id>/promotion` accepting exactly the approved `patch_sha256`. Recompute and compare the patch immediately before mutation. Stale/mismatched proposals fail closed.

### REQ-006
Before promotion, rerun the repository `full` validation profile inside the existing Docker sandbox against the isolated workspace with no network, host home, or Docker socket. Validation failure prevents promotion.

### REQ-007
Promotion creates a deterministic `lai/promotion-<run-id>` branch and a durable Git worktree under the LAI data directory from the recorded source SHA, then applies the exact patch with `git apply --check` followed by `git apply`, all with `shell=False`. The source checkout working tree and HEAD remain unchanged.

### REQ-008
After apply, recompute the promoted worktree patch and require the same SHA-256. Record promoted branch/path/hash/time and validation evidence. A repeated request with the same hash is idempotent; a different hash is rejected.

### REQ-009
No commit, push, merge, release, protected-branch write, arbitrary branch name, arbitrary target path, shell command, or model call is part of promotion.

### REQ-010
Add regression tests for path parsing, failed-run rejection, source drift/dirty rejection, hash mismatch, validation failure, successful promotion, source-checkout invariance, exact promoted diff, idempotency, route/method/body allowlists, and no model invocation.

## Acceptance Criteria
- A successful isolated work run can expose a deterministic promotion proposal.
- Approval is bound to exact patch bytes via SHA-256.
- Promotion produces a dedicated feature worktree/branch, never edits the active source checkout.
- Any source drift, workspace drift, validation failure, or hash mismatch blocks mutation.
- Failed/cancelled runs cannot be promoted.

## Validation
- `REQ-001` / `REQ-003`: proposal/path/patch tests, failed-run rejection, and bounded complete-patch hash checks.
- `REQ-002`: immutable parent-captured source baseline plus dirty/SHA/branch drift and mutable-metadata tamper tests.
- `REQ-004` / `REQ-005`: authenticated GET/POST promotion route, exact-body/method allowlist, hash mismatch, and stale-proposal tests.
- `REQ-006`: existing Docker sandbox tests plus promotion validation-failure regression and real Docker promotion smoke.
- `REQ-007` / `REQ-008`: real Git worktree/apply/hash/idempotency tests and source-checkout invariance assertions.
- `REQ-009`: negative tests prove no model call, commit, push, merge, release, arbitrary branch/path, or shell input.
- `REQ-010`: `tests/test_control_plane.py`, full `make test-dev`, `make test`, Harness Score L4, and `make validate`.

## Context and Constraints
Beta.14 already isolates remote work in disposable safe workspaces and exposes bounded diff evidence. Promotion must not trust that display diff or mutable workspace metadata, and it must not write into the checkout currently open in VS Code. The control server owns the authoritative pre-model source baseline.

## Non-Goals
- No commit/push/PR automation yet.
- No Telegram/PWA approval UI in this core cut.
- No persistent chat sessions, web tools, or MCP.
- No direct application into `main`, `master`, or the active checkout.

## Implementation Notes
Build the exact patch from Git plumbing/porcelain with NUL-delimited path handling. Treat the bounded run diff as presentation only. Promotion is a deterministic core operation with no model turn: revalidate the original workspace, compare the approved SHA-256, create a fixed `lai/promotion-<run-id>` branch/worktree from the recorded source SHA, apply with `git apply --check` then `git apply`, and rehash before recording success.

## Traceability
- `REQ-001` -> `control_promotion_proposal`, terminal/mode/patch gates, failed-run tests.
- `REQ-002` -> parent-captured `source_sha` / `source_branch` / `source_clean`, baseline and metadata-tamper tests.
- `REQ-003` -> structured changed-path inventory and `control_workspace_patch_bytes`; first-path regression test.
- `REQ-004` -> `GET /v1/runs/<id>/promotion` handler and proposal route tests.
- `REQ-005` -> `POST /v1/runs/<id>/promotion`, exact `patch_sha256` body, stale/hash mismatch tests.
- `REQ-006` -> `_run_control_promotion_validation`, Docker sandbox backend, validation-failure and real Docker smoke evidence.
- `REQ-007` -> deterministic promotion branch/worktree path, `git worktree add`, `git apply --check`, `git apply`, source invariance tests.
- `REQ-008` -> post-apply rehash, promotion record fields, same-hash idempotency test.
- `REQ-009` -> fixed branch/path/argv implementation and negative route/no-model/no-Git-publication assertions.
- `REQ-010` -> promotion regression suite, 200-test full suite, 68 pytest subtests, L4 and publication gates.
