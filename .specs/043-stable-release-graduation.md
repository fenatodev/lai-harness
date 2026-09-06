# Spec: stable release graduation

## Metadata
- Mode: `full`
- Status: `complete`
- Target: `0.4.0 stabilization milestone`

## Goal
Make the existing deterministic release pipeline correctly support both pre-release targets and stable semantic-version targets so the project has a governed path from beta to `v0.4.0` without weakening protected-main, artifact, or digest checks.

## Context and Constraints
- The current release-check target/tag state machine is mostly version-agnostic.
- Release-pack fallback copy, GitHub release verification, manual actions, and copied publication documentation still assume every target is a beta/pre-release.
- A stable `v0.4.0` must require GitHub `prerelease=false`; beta/alpha/rc targets must continue requiring `prerelease=true`.
- This spec prepares the path only. It must not change the public version from `0.4.0-beta.24` or publish a stable release.

## Requirements
### REQ-001
**Release-channel classification**
Classify semantic-version targets with a prerelease suffix (alpha/beta/rc or other SemVer prerelease identifier) as pre-release and a plain semantic version such as `0.4.0` as stable.

### REQ-002
**Channel-aware local pack**
Expose release channel/expected prerelease state in release-pack evidence and ensure fallback release body language is correct for pre-release versus stable targets.

### REQ-003
**Channel-aware GitHub verification**
Remote governance must require `prerelease=true` for pre-release targets and `prerelease=false` for stable targets while continuing to require the expected tag, non-draft publication, and optional VSIX digest match.

### REQ-004
**Channel-aware manual actions**
Human action guidance must say pre-release only for prerelease targets and must explicitly avoid the pre-release flag for stable targets.

### REQ-005
**Channel-neutral publication documentation**
Release checklist, release-pack, governance, preflight, publishing, readiness, and README guidance must describe both channels without embedding a beta-only instruction into a future stable pack.

### REQ-006
**Explicit stable exit criteria**
Add a stable-readiness document that defines the finite criteria for graduating the stabilization milestone to `v0.4.0` and clearly classifies PWA/Telegram persistence, read-only web tools, MCP broker, broader provider support, and other roadmap expansion as post-core unless evidence promotes them to blockers.

### REQ-007
**Regression and safety**
Keep the current beta.24 release behavior compatible, preserve protected-main/digest/read-only governance, pass focused and full local gates, and perform no push/PR/tag/release mutation.

## Acceptance Criteria
- `0.4.0-beta.24` and representative alpha/rc versions classify as pre-release; `0.4.0` classifies as stable.
- a mocked GitHub beta release with `prerelease=true` verifies, while a stable target verifies only with `prerelease=false`;
- digest mismatch still fails independently of channel;
- release-pack payload records channel and expected prerelease state;
- fallback body never calls a stable target beta/experimental;
- copied publication docs are valid for either channel;
- `docs/STABLE-READINESS.md` supplies a finite, auditable graduation gate;
- public runtime/extension version remains `0.4.0-beta.24` and no remote mutation occurs.

## Validation
- `REQ-001`: focused unit tests for pre-release/stable classification.
- `REQ-002`: release-pack fallback/payload tests for beta and stable targets.
- `REQ-003`: mocked GitHub release tests for matching/mismatching prerelease flags plus digest checks.
- `REQ-004`: manual-action tests for beta and stable wording.
- `REQ-005`: publication-surface tests and publication scan.
- `REQ-006`: inspect stable-readiness criteria and README/roadmap links.
- `REQ-007`: run release-focused regressions and the full local milestone gate.
- Full local milestone gate: `make milestone-gate` (Ruff + pytest + Harness Score + the publication gate, with overlapping unittest/type/static work executed only once).

## Non-Goals
- Do not bump VERSION/package version to `0.4.0` in this spec.
- Do not create a stable release, tag, PR, or push.
- Do not change required GitHub branch-protection checks.
- Do not add signing/provenance, marketplace publishing, model redistribution, web/MCP/PWA features, or automatic release mutation.
- Do not weaken the requirement that final integration occurs through protected main and post-merge/tag CI.

## Implementation Notes
- Derive channel from the normalized target version rather than from mutable release-note prose.
- Keep compatibility for existing callers of `github_release_status`; target version may be supplied explicitly by governance and otherwise inferred from the expected tag.
- Prefer generic “release” wording in shared docs, adding channel-specific instructions only where the target is known.
- Stable readiness is a scope boundary as much as a checklist: deferred roadmap capabilities must not silently become graduation blockers.

## Traceability
- `REQ-001` -> release-channel helper(s) and tests.
- `REQ-002` -> release pack body/payload and tests.
- `REQ-003` -> GitHub release verification and remote-governance tests.
- `REQ-004` -> manual actions and focused tests.
- `REQ-005` -> shared release/publication docs and publication-surface tests.
- `REQ-006` -> `docs/STABLE-READINESS.md`, README, and roadmap.
- `REQ-007` -> full regression/publication gates and unchanged public version/remote state.


## Validation Evidence

- Release targets now classify deterministically as `prerelease` or `stable` from normalized version semantics; current beta.24 behavior remains pre-release-compatible.
- Release-pack and remote GitHub governance expose/verify the expected prerelease flag; stable targets require `prerelease=false`, and digest mismatch still blocks independently of channel.
- Shared release/publishing documentation is channel-neutral, while `docs/STABLE-READINESS.md` defines a finite graduation boundary and explicitly defers non-core roadmap scope.
- Added `make milestone-gate` as the canonical non-redundant expensive local gate: Ruff + pytest + Harness Score + the publication gate, with unittest/type/static work executed once. Release preflight prefers this target when available and keeps a fallback for older repositories.
- Focused release/process regressions passed: 10 tests. Ruff, strict mypy (5 files), compile/static checks, and diff checks passed.
- Full `make milestone-gate` passed in 123.97s: 254 pytest + 85 subtests, Harness Score L4 100/108 (93%), 254 unittest, strict mypy, publication scan, VSIX packaging and inspection.
- The prior overlapping full-gate sequence was about 180s on this machine; the aggregate gate reduced observed wall time by roughly 31% without removing a validation category.
- Public runtime and extension versions remain `0.4.0-beta.24`; no push, PR, merge, tag, or GitHub Release mutation occurred.
