# Spec: Release notes correctness

## Metadata
- Mode: `full`
- Status: `complete`

## Goal
Make release packs derive their title and GitHub body from the exact target-version section in `docs/RELEASE-NOTES.md`, eliminating stale cross-release metadata.

## Requirements
### REQ-001
Select release notes only from an exact `## lai harness v<TARGET>` section, bounded by the next level-2 heading.

### REQ-002
Generate the release-body artifact from that target section and ignore legacy `### Release body for GitHub` markers in older releases.

### REQ-003
Derive the annotated-tag message from the same target heading; use a safe generic fallback only when the target section is absent.

### REQ-004
Release/publication documentation for the current beta must describe the current beta rather than inherited prior-beta scope.

### REQ-005
Runtime authority, model behavior, remote capabilities, persistence formats, and dependency surface remain unchanged.

## Acceptance Criteria
- A target beta section wins even when an older legacy release-body marker exists later in the file.
- `release-body.md` contains only the target release section.
- `human-release-commands.sh` uses the target release heading for the annotated tag message.
- Prefix-collision versions such as `beta.1` and `beta.10` cannot match each other.
- Full release/publication regression gates stay green.

## Validation
- `REQ-001/002/003`: focused release-pack regression tests.
- `REQ-004`: public publishing-surface regression tests.
- `REQ-005`: full pytest/unittest/publication gates.

## Context and Constraints
Release metadata is publication evidence. A stale body or tag title can misrepresent a correct binary, so the pack must fail predictably or use a neutral fallback rather than copy unrelated release text.

## Non-Goals
- No new release authority or automatic publishing.
- No changes to GitHub branch protection.
- No runtime/session/MCP/subagent feature work.

## Traceability
- `REQ-001/002/003` -> `src/local-agent`, `tests/test_local_agent.py`.
- `REQ-004` -> current release docs and publishing-surface tests.
- `REQ-005` -> existing full validation gates.

## Validation Evidence
- Focused release-pack/identity regressions: 4 passed; install smoke: 2 passed.
- Full pytest: 218 passed + 72 subtests.
- Full unittest publication path: 218 passed.
- Ruff, strict mypy, compile/static checks, and `git diff --check`: green.
- Harness maturity no-regression gate: L4, 100/108.
- Publication scan and VSIX inspection: green.
