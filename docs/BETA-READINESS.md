# Beta readiness

This document records the release posture for `0.4.0-beta.24`. This is a structural-hardening cut that starts incremental decomposition of the 13k+ line runtime without changing operational authority.

## Scope

`0.4.0-beta.24`:

- extracts semantic code-contract data, rendering, and semantic-reference matching into typed `src/lai_semantics.py`;
- keeps `lai semantics` and semantic context ranking behavior compatible and model-free;
- adds `semantic-code-contracts` as a canonical repository-navigation subsystem;
- installs the extracted module beside `local-agent` with no Python package manager or runtime dependency;
- extends the strict mypy ratchet to the first extracted runtime module;
- records the pattern for future incremental subsystem extraction.

No policy, model, network, control-plane, Git, update-apply, or release authority changes in this cut.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.24 --json
lai semantics --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 040 complete, source-tree and installed-runtime semantic regressions green, the strict mypy file set includes `src/lai_semantics.py`, release metadata aligned with beta.24, full Python 3.11/3.12 and publication gates green, and `release-check.phase=ready_for_integration`.

## Protected-main integration

1. Push `feature/v0.4.0-beta.24-semantic-contract-modularization`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`.
4. Merge without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and wait for merged-main CI.
6. Require `lai release-check --target 0.4.0-beta.24 --json` to report `ready_to_tag` before tagging.
7. Freeze the final VSIX, wait for tag CI, then publish the exact pre-release artifact.

The beta.24 change is a maintainability boundary: extracted code must remain behaviorally compatible, dependency-free, typed, and discoverable through the semantic contract.
