# Spec: Beta.1 Release Readiness

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Prepare `0.4.0-beta.1` as the first beta stabilization release after the alpha readiness, diagnostic, run export, and release preflight work.

## Requirements

### REQ-001

The public version must be `0.4.0-beta.1` in the CLI and VS Code extension metadata.

### REQ-002

Release posture documentation must describe the beta.1 scope, validation gate, non-goals, and remaining risks.

### REQ-003

`lai release-check --target 0.4.0-beta.1 --json` must remain deterministic, read-only, and suitable as the final pre-tag gate.

### REQ-004

Existing readiness, run-history, run-export, diagnostic skill, and release preflight behavior must keep passing regression and install smoke coverage.

## Acceptance Criteria

- `lai version` reports `lai harness 0.4.0-beta.1`.
- `lai release-check --target 0.4.0-beta.1 --json` emits parseable JSON with `expected_tag` set to `v0.4.0-beta.1`.
- `docs/BETA-READINESS.md` exists and documents the local and GitHub gates.
- Full validation passes before release commands are suggested.

## Validation

- `REQ-001`: `lai version` and `vscode-extension/package.json` inspection.
- `REQ-002`: review `docs/BETA-READINESS.md`, `CHANGELOG.md`, and roadmap updates.
- `REQ-003`: `lai release-check --target 0.4.0-beta.1 --json`.
- `REQ-004`: `make check`, `make test-dev`, `make test`, and `make validate`.

## Context and Constraints

This release must not introduce new autonomous behavior. Git tagging, merging, pushing, package publishing, and upload remain human-run operations.

## Non-Goals

- Automatic release execution.
- Signed release artifacts.
- Stronger shell sandbox.
- Model download or provider management.
- New cloud or web integrations.

## Implementation Notes

Keep changes focused on version promotion, beta readiness documentation, changelog/roadmap updates, and tests that assert the new version target.

## Traceability

- `REQ-001` -> version and package metadata checks.
- `REQ-002` -> beta readiness documentation review.
- `REQ-003` -> release-check JSON smoke.
- `REQ-004` -> full validation suite and install smoke.
