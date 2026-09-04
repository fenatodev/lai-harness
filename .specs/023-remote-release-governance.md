# Spec: Remote release governance

## Metadata

- Mode: `full`
- Status: `accepted`

## Goal

Verify completed GitHub release governance from `lai release-governance` without granting the command any GitHub write or publication capability.

## Requirements

### REQ-001

Add opt-in `--remote`; default governance remains local/offline.

### REQ-002

Resolve supported github.com `origin` URLs and use credentials from `GH_TOKEN`, `GITHUB_TOKEN`, or non-interactive `git credential fill` without rendering secrets.

### REQ-003

Verify `main` requires PRs, strict required checks, linear history and admin enforcement, with force pushes and deletions disabled.

### REQ-004

Verify the expected GitHub Release is a published pre-release and compare an attached VSIX SHA-256 when both local and remote digests exist.

### REQ-005

Keep all remote operations GET-only, model-free, and repository-read-only; verified GitHub items leave `manual_actions`, while missing or unverified items remain actionable.

### REQ-006

Document the protected-main release flow: feature branch -> PR -> CI -> merge -> main CI -> tag -> tag CI -> pre-release.

## Acceptance Criteria

- `lai release-governance` performs no network request unless `--remote` is present.
- Current protected `main` policy can be reported as `ok` from authenticated GitHub state.
- A published pre-release can be reported as `ok`; a matching VSIX digest is reported explicitly.
- Missing credentials/API access fails closed as `unverified` without exposing secrets.
- No governance code path performs mutation or uses a model.

## Validation

- `REQ-001`: parser/offline governance tests plus `make test-dev`.
- `REQ-002`: GitHub origin resolution and credential-source tests.
- `REQ-003`: branch-protection policy unit test and real GET-only smoke.
- `REQ-004`: pre-release/VSIX digest unit test and real beta.7 smoke.
- `REQ-005`: manual-action clearing/unverified tests plus `make check`.
- `REQ-006`: publication-surface tests plus `make validate`.

## Context and Constraints

`v0.4.0-beta.7` made branch protection and GitHub Release publication explicit manual actions. Those actions are now completed, but local governance cannot distinguish completed state from pending state. The existing Git credential helper is allowed only as a read credential source and must never be printed.

## Non-Goals

- No branch-protection mutation.
- No PR creation or merge.
- No tag, push, asset upload, GitHub Release creation, or publication.
- No mandatory network dependency for default governance.

## Implementation Notes

Use Python standard-library HTTP only. Authenticate opportunistically, keep the public API base overrideable for testing, and represent unavailable remote evidence as `unverified` rather than guessing.

## Traceability

- `REQ-001` -> argument parser and offline governance regression coverage.
- `REQ-002` -> GitHub origin/token helpers and parser tests.
- `REQ-003` -> branch-protection policy helper and unit test.
- `REQ-004` -> release/VSIX helper, real beta.7 smoke, and digest unit test.
- `REQ-005` -> remote collector, safety text, and manual-action tests.
- `REQ-006` -> `docs/RELEASE-CHECKLIST.md`, release notes, publishing metadata, and roadmap.
