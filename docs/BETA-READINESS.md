# Beta readiness

This document records the release posture for `0.4.0-beta.21`. This is an update-intelligence cut: it adds read-only maintenance evidence without adding update/apply authority.

## Scope

`0.4.0-beta.21` adds:

- versioned trusted-source manifest under `updates/`;
- deterministic offline `lai update plan`;
- explicit `lai update check --remote` against fixed official metadata hosts;
- PyPI current/latest and exact-version vulnerability evidence;
- Harness Score version observation;
- authenticated local llama.cpp build observation plus manual compatibility-review classification;
- Dependabot-aware GitHub Actions status;
- release observation for Codex, Claude Code, Qwen Code, Kimi Code, and Hermes Agent;
- bounded/hash-bound untrusted release-note evidence;
- durable change detection under `$LAI_DATA_DIR/update-intelligence`.

No update, model, skill, package, Git ref, PR, or release is applied automatically.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.21 --json
lai update plan --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 037 complete, focused update-intelligence/network-boundary/install regressions green, current release metadata aligned with beta.21, full Python 3.11/3.12 and publication gates green, and `release-check.phase=ready_for_integration`.

A live `lai update check --remote` is dogfood evidence, not a CI dependency; CI uses mocked public metadata and never depends on upstream availability.

## Protected-main integration

1. Push `feature/v0.4.0-beta.21-update-intelligence`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`.
4. Merge without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and wait for merged-main CI.
6. Require `lai release-check --target 0.4.0-beta.21 --json` to report `ready_to_tag` before tagging.
7. Freeze the final VSIX, wait for tag CI, then publish the exact pre-release artifact.

After beta.21 is released, candidate updates discovered by the radar must enter a separate spec/branch/validation cycle. The radar itself never promotes them.
