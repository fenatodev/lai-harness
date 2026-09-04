# Spec 017: beta.2 release polish

## Status

Complete.

## Objective

Prepare `0.4.0-beta.2` as a release-polish beta after the first beta readiness cut. This release should improve the public publishing surface without expanding autonomous agent power.

## Requirements

### REQ-001: beta.2 version identity

The public version must be `0.4.0-beta.2` in the CLI and VS Code extension metadata.

### REQ-002: current GitHub publishing metadata

Publishing metadata must use the current `lai-harness` repository identity and avoid stale first-release notes.

### REQ-003: release notes and checklist

The repository must include ready-to-paste release notes and a manual checklist for GitHub Release creation.

### REQ-004: public artifact naming

Default generated VSIX artifact names must use `lai-harness` while compatibility identifiers remain preserved.

### REQ-005: deterministic gates stay read-only

`lai release-check --target 0.4.0-beta.2 --json` must remain deterministic, read-only, and suitable as the final pre-tag gate.

## Validation

- `lai version` reports `lai harness 0.4.0-beta.2`.
- `lai release-check --target 0.4.0-beta.2 --json` emits parseable JSON with `expected_tag` set to `v0.4.0-beta.2`.
- `make check` passes.
- `make validate` passes.
- Installed smoke verifies readiness, release-check, run export, and doctor.

## Traceability

- `REQ-001` -> version tests and install smoke.
- `REQ-002` -> publishing metadata regression test.
- `REQ-003` -> docs/RELEASE-NOTES.md and docs/RELEASE-CHECKLIST.md.
- `REQ-004` -> package script regression test.
- `REQ-005` -> release-check regression test.

## Non-goals

- Do not add web search, cron, plugin execution, automatic model downloads, sandbox claims, automatic Git mutation, or marketplace publication.
