# Beta readiness

This document records the release posture for `0.4.0-beta.20`. This is an automated model-evaluation cut. It adds measurement capability but does not change the configured default model or expand repository/remote authority.

## Scope

`0.4.0-beta.20` adds:

- versioned disposable model-evaluation fixtures;
- `lai model run` against only the already-loaded authenticated endpoint model;
- isolated state/metrics/audit streams for every scenario;
- independent machine validation for model-backed fixtures;
- automatic hallucination flags for objective claim/evidence mismatches;
- repeatable samples with decision-eligibility rules;
- model/server/hardware, executable, fixture, and Git provenance;
- multi-file scoring plus `latest` local result resolution;
- installed fixture synchronization under `$LAI_DATA_DIR/model-eval`;
- the first recorded Ministral/Qwen local bake-off.

No model is downloaded, started, stopped, switched, fine-tuned, or selected automatically.
## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.20 --json
lai model plan --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 036 complete, model-evaluation regressions green, install smoke proving fixture availability, full Python 3.11/3.12 and publication gates green, and `release-check.phase=ready_for_integration`.

Automated live-model runs are dogfood evidence, not CI requirements; CI never depends on a local model server.

## Protected-main integration

1. Push `feature/v0.4.0-beta.20-automated-model-evaluation`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`.
4. Merge without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and wait for merged-main CI.
6. Require `lai release-check --target 0.4.0-beta.20 --json` to report `ready_to_tag` before tagging.
7. Freeze the final VSIX, wait for tag CI, then publish the exact pre-release artifact.
