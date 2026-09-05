# Beta readiness

This document records the release posture for `0.4.0-beta.23`. This is an update-evidence convergence cut discovered by beta.22 dogfooding: stale persisted observations must never be presented as current maintenance advice after the local LAI/update-source baseline changes.

## Scope

`0.4.0-beta.23` adds:

- deterministic offline freshness checks for the persisted update snapshot;
- comparison of snapshot LAI version and source-manifest SHA-256 against the current trusted local baseline;
- `overall=refresh_required` when either baseline is missing or differs;
- explicit reason codes plus `lai update check --remote` as the operator refresh action;
- suppression of stale per-source security, compatibility, and maintenance recommendations;
- preservation of beta.22 security-first triage semantics after evidence converges;
- traceability cleanup for the already-completed release-governance spec 021.

No network refresh, dependency update, model call, Git mutation, PR, tag, or release action is performed automatically.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.23 --json
lai update plan --json
lai update triage --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```
Expected before merge: spec 039 complete, focused freshness regressions green, real stale→refresh→fresh dogfood recorded, release metadata aligned with beta.23, full Python 3.11/3.12 and publication gates green, and `release-check.phase=ready_for_integration`.

The live dogfood path must prove that triage remains offline while stale and only converges after an explicit remote check.

## Protected-main integration

1. Push `feature/v0.4.0-beta.23-update-evidence-convergence`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`.
4. Merge without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and wait for merged-main CI.
6. Require `lai release-check --target 0.4.0-beta.23 --json` to report `ready_to_tag` before tagging.
7. Freeze the final VSIX, wait for tag CI, then publish the exact pre-release artifact.

The beta.23 change is evidence hygiene, not update authority: stale observations trigger a deterministic refresh requirement and cannot silently become current actions.