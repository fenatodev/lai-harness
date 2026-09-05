# Spec: Update evidence convergence

## Metadata

- Mode: `full`
- Status: `complete`
- Target: `0.4.0-beta.23`

## Goal

Prevent offline update triage from presenting a persisted snapshot from an older local LAI/update-source baseline as current maintenance advice.

## Context and Constraints

- Beta.22 dogfooding showed that a pre-release snapshot can survive an install and briefly report an already-adopted dependency as pending.
- A new explicit remote check correctly converges the evidence, so the problem is stale local evidence rather than incorrect upstream detection.
- Persisted update summaries already include the LAI version and update-source manifest SHA-256 needed for deterministic convergence checks.
- Triage must remain offline, model-free, fail-closed, and unable to mutate dependencies, repositories, Git refs, releases, or configuration.

## Requirements

### REQ-001

`lai update triage` must compare the persisted snapshot version and manifest SHA-256 with the currently running LAI version and current trusted update-source manifest without network access.
### REQ-002

If either baseline value is missing or differs, triage must report `overall=refresh_required`, mark the evidence stale with deterministic reason codes, and suppress stale per-source maintenance/security/compatibility actions.

### REQ-003

Stale triage must expose the explicit operator action `lai update check --remote` but must never invoke it automatically. It must keep `automatic_apply=false`, `model_call=false`, and automatic refresh disabled.

### REQ-004

When snapshot version and manifest hash match the running baseline, existing beta.22 security-first triage semantics, ordering, reason codes, and actions must remain unchanged.

### REQ-005

JSON and human-readable output must expose evidence freshness without including upstream release-note prose in priority or freshness decisions.

### REQ-006

Regression coverage must reproduce the beta.22 dogfood case: an older snapshot yields `refresh_required`; a fresh matching snapshot yields normal triage; two repeated fresh observations remain stable.

### REQ-007

Close the stale textual status in spec 021 as completed so repository traceability does not imply unfinished release-governance work.

## Acceptance Criteria

- Offline triage detects old-version and old-manifest snapshots deterministically.
- Stale snapshots do not emit actionable per-source recommendations.
- Fresh snapshots preserve beta.22 triage behavior.
- No network request or model call occurs during triage.
- The explicit refresh command remains operator-triggered.
- Focused tests, full validation, and real dogfood converge cleanly.

## Validation

- `REQ-001`: offline triage regression comparing persisted LAI version/manifest hash with the running baseline.
- `REQ-002`: stale-version, stale-manifest, and missing-baseline regressions asserting `refresh_required` and suppressed source actions.
- `REQ-003`: regression asserting explicit `lai update check --remote` guidance with no automatic refresh/apply/model call.
- `REQ-004`: matching-baseline regression preserving beta.22 security-first triage semantics and ordering.
- `REQ-005`: JSON/text freshness-output regressions and release-note exclusion checks.
- `REQ-006`: beta.22-to-beta.23 stale snapshot dogfood followed by one explicit remote refresh and repeated stable fresh triage.
- `REQ-007`: `test_current_active_spec_passes_runtime_validation` plus repository inspection confirming spec 021 is complete and no stale active spec remains.
- Full gates: `make check`, `make test-dev`, `make test`, `make harness-score-gate`, `make validate`.

## Validation Evidence

- Focused update-intelligence suite: 23 passed + 13 pytest subtests.
- High-risk update/core/install group: 150 passed + 79 pytest subtests.
- Full pytest after final spec closure and active-spec gate: 249 passed + 85 subtests.
- Final publication validation after spec closure: 249 dependency-free unittest tests passed.
- Ruff and strict mypy are green; deterministic compile/static/Git-diff checks are green.
- Harness Score 1.6.4 remains L4 Self-correcting at 100/108 (93%).
- Final publication scan is clean and VSIX inspection passed.
- Real dogfood: beta.22 snapshot under beta.23 runtime returned `refresh_required`, suppressed stale source actions, and exposed only explicit `lai update check --remote`; one operator-triggered check converged the snapshot and restored normal triage.
- Repeated fresh observations remained stable; the existing llama.cpp compatibility/manual-review signal was preserved.

## Non-Goals

- No TTL/time-based staleness policy in this cut.
- No automatic network refresh.
- No automatic dependency/runtime/model update.
- No llama.cpp upgrade decision.
- No MCP, web, browser, subagent, provider, commit, push, merge, tag, PR, or publication authority.

## Implementation Notes

Prefer one deterministic freshness helper reused by JSON and text rendering. Treat missing baseline metadata as stale for backward compatibility with older persisted records. Preserve the old observations only as source provenance; do not convert them into current actions when freshness fails.

## Traceability

- `REQ-001` -> `update_triage_evidence_status`, local manifest loading, and offline triage regressions.
- `REQ-002` -> stale-evidence branch in `build_update_triage` plus stale-version/manifest/missing-metadata regressions.
- `REQ-003` -> explicit refresh metadata/safety flags and no-auto-refresh regression.
- `REQ-004` -> matching-baseline triage path and beta.22 semantic-preservation regression.
- `REQ-005` -> JSON payload, `render_update_triage`, and release-note exclusion coverage.
- `REQ-006` -> regression fixtures plus real beta.22-to-beta.23 dogfood evidence.
- `REQ-007` -> `.specs/021-release-governance.md` status cleanup and `test_current_active_spec_passes_runtime_validation`.
