# Spec: Update triage

## Metadata

- Mode: `full`
- Status: `complete`
- Target: `0.4.0-beta.22`

## Goal

Turn the beta.21 update radar into deterministic maintenance triage without granting update authority, and dogfood the first low-risk candidate by moving Harness Score from 1.6.3 to 1.6.4 only after equivalence is proven.

## Context and Constraints

- Beta.21 is released and installed; this cut starts from protected synchronized `main`.
- Triage consumes only persisted structured update evidence.
- Upstream release-note text remains untrusted and must not influence priority.
- Runtime remains Python standard-library-only.
- No update/apply/install/download/commit/push/merge/tag/release authority is added.

## Requirements

### REQ-001
**Offline triage.** `lai update triage [--json]` reads only the latest persisted update-intelligence snapshot and performs no network request, model call, package-manager action, repository mutation, or Git mutation.
### REQ-002
**Structured priority.** Triage assigns deterministic priority, urgency, action, reason codes, and update scope from structured metadata only.

### REQ-003
**Security first.** Known vulnerability evidence outranks compatibility, maintenance, managed, reference, and current observations.

### REQ-004
**Untrusted notes excluded.** Upstream release-note text never influences priority and never appears in the triage payload.

### REQ-005
**Version scope.** Comparable numeric versions distinguish patch, minor, major, revision, and no-change. Incomparable schemes remain manual-review signals.

### REQ-006
**Governed sensor update.** Harness Score 1.6.4 is adopted only after 1.6.3 and 1.6.4 produce equivalent L4/100 results and successful exits on the same repository.

### REQ-007
**Synchronized pins.** The Harness Score version stays synchronized across Makefile commands, the SHA-pinned GitHub Action release, update manifest, verification workflow, and current documentation. Tests fail on drift.

### REQ-008
**No update authority.** `lai update` still exposes no apply, install, download, upgrade, commit, push, merge, tag, PR, or publication operation.
## Acceptance Criteria

- `lai update triage --json` works with server/network unavailable.
- Security observations sort ahead of maintenance candidates.
- A patch update classifies as maintenance/low.
- Malicious-looking release-note text cannot affect or enter triage output.
- Harness Score 1.6.4 reports L4 / 100/108 (93%) with exit 0.
- Current operational pins all resolve to reviewed Harness Score 1.6.4 sources.
- Full validation and publication gates remain green.

## Implementation Notes

- Keep triage local-only; do not persist a second derived state unless later evidence justifies it.
- Base priority only on trusted structured fields already captured by beta.21.
- Sort by urgency first, then priority, then stable source id.
- Pin the Harness Score GitHub Action to the exact v1.6.4 release commit, not the moving `v1` tag.
- Keep historical release/spec references to earlier Harness Score versions unchanged.

## Non-Goals

- Automatic updates or pull requests.
- Parsing release-note prose as executable policy.
- Generic vulnerability scoring beyond metadata already provided by trusted sources.
- Resolving llama.cpp build/tag compatibility automatically.
## Traceability

- `REQ-001` -> `render_update_triage`, CLI local-only boundary, no-network regression.
- `REQ-002` -> `triage_update_record`, `build_update_triage`, deterministic ordering tests.
- `REQ-003` -> vulnerability-first triage regression.
- `REQ-004` -> release-note injection regression and triage payload allowlist.
- `REQ-005` -> `update_change_scope` tests for patch/minor/major/incomparable schemes.
- `REQ-006` -> recorded 1.6.3 versus 1.6.4 equivalence run plus L4 gate.
- `REQ-007` -> synchronized-pin regression across Makefile, Action SHA, manifest, workflow, and docs.
- `REQ-008` -> forbidden update CLI verbs regression.

## Validation

- `REQ-001`: local-only triage CLI regression with network/model paths unavailable.
- `REQ-002`: deterministic priority/urgency/action/reason ordering regression.
- `REQ-003`: vulnerability-first ordering regression.
- `REQ-004`: malicious release-note text exclusion regression.
- `REQ-005`: patch/minor/major/incomparable version-scope regression.
- `REQ-006`: same-repository Harness Score 1.6.3 versus 1.6.4 equivalence plus L4 gate.
- `REQ-007`: synchronized pin regression across Makefile, Action SHA, manifest, verification workflow, and docs.
- `REQ-008`: forbidden update CLI verbs regression.
- Full gates: `make lint`, `make typecheck`, `make check`, `make test-dev`, `make test`, `make harness-score-gate`, `make validate`.
- Publication scan and VSIX inspection.

## Validation Evidence

- Focused update-intelligence/triage regressions: 18 passed; grouped update/action/quality regressions: 26 passed.
- Harness Score 1.6.3 and 1.6.4 equivalence: both L4 Self-correcting, 100/108 (93%), exit 0.
- Harness Score 1.6.4 gate: L4 Self-correcting, 100/108 (93%).
- Full pytest: 243 passed + 85 subtests.
- Full unittest: 243 passed.
- Ruff, strict mypy, compile/static checks, and Git diff checks are green.
- Publication scan is clean and VSIX inspection passed.
- Semantic subsystem contract is unique: 19 ids / 19 unique.