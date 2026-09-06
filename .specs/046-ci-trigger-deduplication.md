# Spec: CI trigger deduplication

## Metadata

- Mode: `quick`
- Status: `complete`

## Goal

Stop the expensive CI workflow from running twice for the same feature-branch commit when a pull request is open, while preserving pull-request validation, post-merge `main` validation, and release-tag validation.

## Requirements

### REQ-001

Scope `.github/workflows/ci.yml` push triggers to `main` and `v*` tags while retaining the existing `pull_request` trigger and all current jobs/check names.

### REQ-002

Add a regression sensor that fails if generic feature-branch push CI is reintroduced or if PR/main/tag coverage is removed.

## Acceptance Criteria

- A feature branch with an open PR is validated by the PR workflow only, not by an additional generic branch-push CI run.
- Pushes to `main` still run CI.
- Pushes of `v*` release tags still run CI.
- Pull requests still run CI and preserve `Python 3.11`, `Python 3.12`, and `Publication gates`.
- Existing immutable Action pins and Harness Score workflow behavior remain unchanged.

## Validation

- `REQ-001`: inspect workflow trigger diff and run GitHub Actions hardening regressions.
- `REQ-002`: run the new trigger regression plus `make check` and `git diff --check`.

## Context and Constraints

The `v0.4.0` release observed duplicate CI runs because `ci.yml` listened to both unrestricted `push` and `pull_request`. Local milestone gates already provide pre-PR feedback, so generic feature-branch push CI has low value relative to its cost.

## Non-Goals

- Do not rename or remove required status checks.
- Do not change branch protection.
- Do not change test, publication, or Harness Score job contents.
- Do not publish a release for this quick spec.

## Implementation Notes

Prefer the smallest YAML trigger change. Keep tag CI because stable release governance requires tag validation before publication.

## Traceability

- `REQ-001` -> `.github/workflows/ci.yml`, `tests/test_github_actions_hardening.py`.
- `REQ-002` -> focused regression and static checks.

## Validation Evidence

- `ci.yml` push scope is limited to `main` and `v*` tags while `pull_request` remains enabled.
- Existing Python 3.11/3.12 and Publication gates job definitions and immutable Action pins are unchanged.
- Focused GitHub Actions/quality-sensor regressions: 10 passed.
- `make check` and `git diff --check` passed.
- No version bump, release, branch-protection change, or remote mutation occurred.
