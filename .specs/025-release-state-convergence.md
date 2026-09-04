# Spec: Release state convergence

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Make release handoff and tag readiness report the same trustworthy state by separating offline and remote governance evidence and by preventing release tagging from a feature branch, a divergent main checkout, or a tag that already points at another commit.

## Requirements

### REQ-001

Add opt-in `--remote` to `lai project-handoff` / `lai next-chat`; the default remains deterministic, model-free, and offline.

### REQ-002

Represent local and remote release governance separately in handoff JSON/Markdown. When `--remote` is enabled, the effective handoff status and manual actions must come from the remotely verified governance result while preserving the local/offline result for auditability.

### REQ-003

Propagate remote branch-protection, GitHub Release, credential-source metadata, and VSIX digest evidence into the handoff without rendering credentials or adding any GitHub write capability.

### REQ-004

Strengthen `lai release-check` so `ready_to_tag` is possible only when the current branch is `main`, `HEAD` equals the local `origin/main` tracking ref, the working tree/readiness gates pass, and the expected release tag does not already point elsewhere.

### REQ-005

Distinguish a clean feature-branch candidate as `ready_for_integration` rather than `ready_to_tag`. If the expected tag already points to another commit, or `main` is not synchronized with `origin/main`, release-check must block tagging. A release is `released` only when the expected tag peels to `HEAD` and main-integration evidence is valid.

### REQ-006

Update release-pack/handoff documentation, beta identity, and automated coverage without making default deterministic commands network-dependent or weakening protected-main release flow.

## Acceptance Criteria

- `lai project-handoff --remote --json` can report remote governance `ready` while also retaining the offline/local governance status.
- Default `lai project-handoff --json` performs no remote GitHub verification.
- A feature branch with a clean candidate reports `ready_for_integration`, never `ready_to_tag`.
- A clean synchronized `main` with no target tag reports `ready_to_tag`.
- A target tag pointing to another commit blocks release-check.
- A divergent or unavailable `origin/main` blocks tagging from `main`.
- Existing published tag at synchronized `main` reports `released` only when it peels to `HEAD`.
- Remote handoff remains GitHub GET-only and never exposes token values.

## Validation

- `REQ-001` / `REQ-002` / `REQ-003`: focused argument/payload/render/write tests with mocked remote governance plus install smoke.
- `REQ-004` / `REQ-005`: repository-state tests covering feature branch, synchronized main, divergent main, correct tag target, and wrong tag target.
- `REQ-006`: `make lint`, `make check`, `make test-dev`, `make test`, `make validate`, and Harness Score L4 gate.

## Context and Constraints

Beta.9 is publicly released at `v0.4.0-beta.9`, main is protected by four required checks, and remote governance verifies the published release as ready. The remaining handoff currently reports the offline governance result (`action_required`) even after remote governance is `ready`. Beta.8 also exposed an operational hazard where a release tag could be created before the intended merged-main commit existed.

## Non-Goals

- Do not make default handoff or release-check network-dependent.
- Do not add GitHub write operations to release-governance or project-handoff.
- Do not add subagents, MCP configuration, type checking, or dependency lockfiles in this beta.
- Do not attempt to prove GitHub Actions completion inside offline `release-check`; CI remains a separate protected release gate.

## Implementation Notes

Keep `release-check` deterministic by using only local Git metadata, including the local `origin/main` tracking ref and peeled target-tag ref. Remote handoff should reuse `collect_release_governance(..., remote=True)` rather than creating another GitHub client path. Preserve backward-compatible summary fields where practical while adding explicit local/remote evidence.

## Traceability

- `REQ-001` -> project handoff CLI parser/router and install smoke.
- `REQ-002` -> project handoff payload and Markdown rendering.
- `REQ-003` -> remote governance evidence propagation and redaction tests.
- `REQ-004` -> release-check main-integration/tag-target checks.
- `REQ-005` -> release phases and repository-state regression tests.
- `REQ-006` -> version/release docs, release-pack title, full validation.
