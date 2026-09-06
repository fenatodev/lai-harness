# Spec: v0.4.0 stable freeze

## Metadata
- Mode: `full`
- Status: `complete`
- Target: `0.4.0`

## Goal
Freeze the validated stabilization milestone as the first stable `v0.4.0` candidate locally, aligning release identity and evidence without adding new product scope or performing GitHub publication actions.

## Context and Constraints
- `3c34609` added channel-aware stable release governance and the non-redundant milestone gate.
- `e394cc7` fixed a dogfooded model-eval result resolution defect.
- Current runtime readiness is `ready`; the baseline model now has 10 records, 5/5 scenarios, minimum two samples per scenario, and `decision_eligible: yes` with a documented review weakness.
- Historical beta specs/release notes must remain historical evidence, not be rewritten as stable work.

## Requirements
### REQ-001
Align runtime, VS Code extension, visual review marker, and current public identity to `0.4.0` / `v0.4.0`.

### REQ-002
Add stable release notes and changelog entries that summarize the shipped core, stabilization changes, known limitations, and unchanged authority boundary.

### REQ-003
Record current repeated baseline-model evidence accurately without claiming universal model superiority or hiding the repeated review weakness.

### REQ-004
Update current release/readiness/handoff examples to target `0.4.0` while preserving historical beta.24 evidence and explicit pre-release compatibility tests.

### REQ-005
Prove locally that release-check/release-pack classify the candidate as `stable` with `expected_prerelease=false`, and that installed/runtime deterministic commands remain compatible.

### REQ-006
Keep scope frozen: no new feature, policy authority, remote shell, update apply, Git mutation, model switching, dependency installation, PR, merge, tag, or publication action.

### REQ-007
Pass focused version/publication/install regressions, then run one final `make milestone-gate` after the freeze diff is stable.

## Acceptance Criteria
- all current-version surfaces report `0.4.0` while historical beta documents remain beta.24;
- `lai release-check --target 0.4.0 --json` reports `release_channel=stable` and `expected_prerelease=false`;
- current public docs no longer describe the active release as experimental beta;
- model-evaluation docs record 10 decision-eligible baseline samples and the repeated review miss;
- tree is clean after a local freeze commit and no GitHub mutation has occurred.

## Validation
- `REQ-001`/`REQ-004`: version/publication/visual/install focused tests.
- `REQ-002`/`REQ-003`: documentation assertions and publication scan.
- `REQ-005`: local release-check/release-pack dogfood for `0.4.0`.
- `REQ-006`: inspect diff and Git state; no remote mutation commands.
- `REQ-007`: focused checks first; one final `make milestone-gate` only after the candidate diff is stable.

## Non-Goals
- Do not publish `v0.4.0` in this spec.
- Do not push the stabilization branch or open/merge a PR.
- Do not add deferred PWA/web/MCP/subagent/marketplace/signing scope.
- Do not change the default model based on this baseline-only evidence.

## Implementation Notes
- Prefer deriving tests from the current runtime version where that reduces needless future version churn; keep explicit beta fixtures where channel behavior is under test.
- Stable release notes should describe the first stable core, not rewrite historical beta entries.
- Run the expensive milestone gate once, at the final local freeze boundary.

## Traceability
- `REQ-001` -> runtime/package/visual marker/current README identity.
- `REQ-002` -> release notes and changelog.
- `REQ-003` -> model-evaluation documentation.
- `REQ-004` -> current release docs and regression fixtures.
- `REQ-005` -> release channel/package dogfood and focused tests.
- `REQ-006` -> diff/Git safety evidence.
- `REQ-007` -> focused regressions plus final milestone gate.


## Validation Evidence

- Canonical runtime, VS Code extension, public README identity, and visual review marker are aligned to `0.4.0`; retained beta.24 specs/release notes remain historical evidence.
- Stable release notes/changelog document the shipped core, finite stable-readiness scope, unchanged authority boundary, and current repeated model evidence without hiding the repeated review validation miss.
- Current baseline model evidence: 10 records, all 5 model-backed scenarios covered with at least 2 samples each, aggregate 90.8/100, `decision_eligible: yes`; `review-supported-findings` remains 55/100 twice with validation failure.
- Focused freeze checks passed: 23 current version/release/model/publication regressions plus 5 install/visual regressions; Ruff, strict mypy over five files, compile/static, and diff checks green.
- Pre-commit `lai release-check --target 0.4.0 --json` identified `release_channel=stable` and `expected_prerelease=false`; blocked state was solely the expected dirty/active-spec freeze state.
- Final `make milestone-gate` passed in 125.29s: 255 pytest + 85 subtests, Harness Score L4 100/108 (93%), 255 unittest, strict mypy, publication scan, VSIX packaging, and VSIX inspection.
- No new product capability, default-model change, push, PR, merge, tag, or GitHub Release mutation occurred during the stable freeze.
