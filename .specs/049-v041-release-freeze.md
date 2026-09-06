# Spec: v0.4.1 release freeze

## Metadata

- Mode: `full`
- Status: `complete`
- Target: `0.4.1`

## Goal

Freeze the validated post-v0.4.0 milestone as `v0.4.1`, aligning public release identity and evidence without adding new product scope before protected integration.

## Requirements

### REQ-001

Align runtime, VS Code extension, visual review marker, README identity, handoff examples, changelog, and release notes to `0.4.1` / `v0.4.1`.

### REQ-002

Document the post-v0.4.0 scope as CI deduplication, persistent remote sessions, and bounded read-only web evidence, with explicit safety boundaries.

### REQ-003

Preserve historical `v0.4.0` and beta release notes/spec evidence without rewriting prior release history.

### REQ-004

Prove `lai release-check --target 0.4.1 --json` reports stable channel, `expected_prerelease=false`, and reaches the appropriate pre-integration phase after the freeze commit.

### REQ-005

Pass focused release/publication/version tests and the full non-redundant milestone gate before any PR, tag, or GitHub Release action.

## Acceptance Criteria

- current-version surfaces report `0.4.1`;
- top release note is `lai harness v0.4.1 — operational capability patch`;
- changelog starts with `[0.4.1]`;
- historical `v0.4.0` evidence remains present below the new entry;
- release-check for target `0.4.1` is stable-channel and no longer blocked by `version_target`;
- no feature code, model configuration, dependency set, branch protection, tag, or release publication changes occur in this spec.

## Validation

- `REQ-001`: version grep, visual/version tests, install smoke expectations.
- `REQ-002`: inspect changelog/release notes and public docs.
- `REQ-003`: publication-surface regression preserving `v0.4.0` history.
- `REQ-004`: local release-check/release-pack dogfood for `0.4.1`.
- `REQ-005`: focused tests, static checks, and `make milestone-gate`.

## Context and Constraints

The post-v0.4.0 branch already contains the validated CI trigger deduplication, persistent remote sessions, and read-only web evidence specs. This freeze must not expand that scope. The release remains stable, not prerelease.

## Non-Goals

- Do not add new runtime features or refactor existing feature code.
- Do not push, open PR, tag, upload, or publish from inside this freeze spec.
- Do not change model defaults, provider support, MCP, marketplace distribution, signing, or release governance policy.

## Implementation Notes

Keep the freeze as release metadata plus tests only. Treat `v0.4.0` references in historical specs and prior release notes as immutable history.

## Traceability

- `REQ-001` -> version files, README/PT-BR, handoff docs, visual marker.
- `REQ-002` -> `CHANGELOG.md`, `docs/RELEASE-NOTES.md`.
- `REQ-003` -> public publication regression.
- `REQ-004` -> `lai release-check` / `lai release-pack` output.
- `REQ-005` -> focused tests and final milestone gate.

## Validation Evidence

- Aligned runtime `VERSION`, VS Code extension package version, README/PT-BR current release identity, project handoff examples, release-governance examples, visual review marker, changelog, and release notes to `0.4.1` / `v0.4.1`.
- Added top release notes entry `lai harness v0.4.1 — operational capability patch` and top changelog entry `[0.4.1] - 2026-09-05`.
- Documented the exact post-v0.4.0 scope: CI trigger deduplication, persistent remote sessions, and bounded read-only web evidence.
- Preserved historical `v0.4.0` stable-core and beta.24 release evidence below the new release entries.
- Focused release/version/publication tests passed: 29 tests, 114 deselected.
- `lai release-check --target 0.4.1 --json` reported `version=0.4.1`, `target_version=0.4.1`, `expected_tag=v0.4.1`, `release_channel=stable`, and `expected_prerelease=false`; blocked state before commit was only the expected dirty active-spec state.
- Ruff, strict mypy over seven files, and static checks passed.
- Full milestone gate passed: 271 pytest tests + 97 subtests, Harness Score L4 100/108 (93%), 271 unittest tests, strict mypy over seven files, publication scan, and VSIX inspection green in 126.95s.
- No feature code, model default, dependency set, branch protection, push, PR, tag, GitHub Release, or publication mutation occurred in this freeze spec.
