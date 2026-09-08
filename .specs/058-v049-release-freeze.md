# Spec: v0.4.9 model-eval evidence freeze

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Freeze the validated post-v0.4.8 work as a local `v0.4.9` release candidate without adding product scope or performing publication actions.

The release should package bounded operational reliability and model-evaluation evidence hardening while preserving the existing authority boundary.

## Requirements

### REQ-001

Bump the canonical runtime and VS Code extension package version from `0.4.8` to `0.4.9`.

### REQ-002

Update current-release README/PT-BR, visual review metadata, changelog, and release notes to target `v0.4.9`.

### REQ-003

Preserve `v0.4.8` as historical release evidence rather than rewriting it away.

### REQ-004

Document the release as evidence hardening and bounded operational reliability, not as MCP execution, browser authority, learning, model switching, or Gateway feature delivery.

### REQ-005

Prove `lai release-check --target 0.4.9 --json` reports stable channel, `expected_prerelease=false`, and the expected `v0.4.9` tag posture.

### REQ-006

Validate with focused current-version/release/public-surface checks and the full `make milestone-gate` before integration.

## Acceptance Criteria

- Runtime and VS Code extension version surfaces report `0.4.9`.
- README, PT-BR README, changelog, release notes, and visual asset metadata identify `v0.4.9` as current release material.
- `v0.4.8` release notes and changelog history remain intact below the new release section.
- Release notes explicitly state disabled authority: no MCP execution, browser automation, mobile writes, automatic updates, model switching, commits, pushes, tags, releases, or remote mutation.
- `lai release-check --target 0.4.9 --json` identifies `release_channel=stable`, `expected_prerelease=false`, and `expected_tag=v0.4.9`.
- Dirty-tree blocking remains expected before the human-approved release-freeze commit.

## Validation

- `REQ-001`: version-focused tests plus deterministic `lai --version` and extension metadata inspection.
- `REQ-002`: public docs, changelog, release-note, and visual-asset tests.
- `REQ-003`: inspect retained `docs/RELEASE-NOTES.md` `v0.4.8` section and changelog history.
- `REQ-004`: inspect release safety boundary text and non-goal list.
- `REQ-005`: run `lai release-check --target 0.4.9 --json` before and after freeze metadata alignment.
- `REQ-006`: run focused version/release/public-surface checks, `make check`, then `make milestone-gate` once the freeze diff is stable.

## Context and Constraints

M1-M4 have local evidence. M5 packages that evidence into a coherent release candidate.

`0.4.9` remains a stable semantic-version target, not a prerelease.

The source tree is expected to be dirty before the freeze commit, so `release-check` may remain blocked on Git status until the human-approved commit/integration boundary.

Direct agent-driven Git mutation remains an `ASK` action and is not performed by this spec.

## Non-Goals

- Publishing the release from this spec.
- Creating a tag, release asset, PR merge, push, or remote branch-protection change locally.
- Implementing MCP execution, mobile writes, Telegram/PWA integration, browser automation, model-provider switching, automatic updates, or learning/autonomous self-modification.
- Changing the default model.

## Implementation Notes

Keep this as a release freeze: align version and public surfaces, add no new runtime capability, and preserve prior release evidence.

## Traceability

- `REQ-001` -> `src/local-agent`, `vscode-extension/package.json`, and version-focused tests.
- `REQ-002` -> `README.md`, `README.pt-BR.md`, `docs/assets/visual-assets.json`, `CHANGELOG.md`, and `docs/RELEASE-NOTES.md`.
- `REQ-003` -> retained `docs/RELEASE-NOTES.md` `v0.4.8` section and changelog history.
- `REQ-004` -> release safety boundary text and non-goal list.
- `REQ-005` -> `lai release-check --target 0.4.9 --json` output.
- `REQ-006` -> focused tests, `make check`, and `make milestone-gate` evidence.


## Validation Evidence

- `lai --version` reports `lai harness 0.4.9` and `vscode-extension/package.json` reports `0.4.9`.
- `docs/assets/visual-assets.json` is reviewed for `0.4.9` and visual asset tests passed.
- `lai release-check --target 0.4.9 --json` reports `version_target=ok`, `release_channel=stable`, `expected_prerelease=false`, `expected_tag=v0.4.9`, and `release_safety=ok`; dirty Git status remains the expected pre-commit blocker.
- Focused version/release/public/model-eval checks passed: 35 passed, 147 deselected.
- `make check` passed after freeze metadata alignment.
- Full `make milestone-gate` passed in 161.64s: Ruff green, pytest 325 passed with 144 subtests, Harness Score L4 103/108, `validate.sh` with 325 unittest tests, strict mypy over seven source files, publication scan clean, package generation, and VSIX inspection passed.
- Final post-evidence check passed: `make check`, plus focused no-active/version/release/public checks with 24 passed and 158 deselected.
- `lai release-pack --target 0.4.9 --with-vsix --json` produced a local pack only at `/tmp/lai-harness-release-pack-v0.4.9`, including `lai-harness-0.4.9.vsix`, and reported no tag, merge, push, upload, publication, model call, or repository file mutation.
- No tag, push, PR merge, GitHub Release, MCP execution, browser automation, mobile write, default-model change, or remote mutation occurred.
