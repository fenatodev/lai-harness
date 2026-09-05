# Beta readiness

This document records the release posture for `0.4.0-beta.22`. This is an update-triage cut: it ranks persisted maintenance evidence and dogfoods one low-risk dependency update without adding update/apply authority.

## Scope

`0.4.0-beta.22` adds:

- local-only `lai update triage` over the latest beta.21 observation;
- deterministic priority, urgency, action, reason codes, and version scope;
- security-first ordering for known vulnerability evidence;
- explicit patch/minor/major/revision classification for comparable numeric versions;
- manual compatibility review for incomparable schemes such as llama.cpp build ids versus semantic tags;
- strict exclusion of untrusted release-note text from triage decisions and payloads;
- Harness Score 1.6.4 adoption after measured equivalence with 1.6.3;
- synchronized Harness Score pins across Makefile, exact Action SHA, manifest, verification workflow, and docs.

No update, model, skill, package, Git ref, PR, or release is applied automatically by `lai update`.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.22 --json
lai update plan --json
lai update triage --jsonmake lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 038 complete, focused update-triage and synchronized-pin regressions green, current release metadata aligned with beta.22, full Python 3.11/3.12 and publication gates green, and `release-check.phase=ready_for_integration`.

The beta.21 live update snapshot is dogfood input for triage. CI never depends on upstream network availability; triage tests use structured local fixtures.

## Protected-main integration

1. Push `feature/v0.4.0-beta.22-update-triage`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`.
4. Merge without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and wait for merged-main CI.
6. Require `lai release-check --target 0.4.0-beta.22 --json` to report `ready_to_tag` before tagging.
7. Freeze the final VSIX, wait for tag CI, then publish the exact pre-release artifact.

Harness Score 1.6.4 is maintenance evidence consumed through this governed flow; future candidates follow the same pattern rather than being auto-applied.