# lai beta readiness

This document records the release posture for `0.4.0-beta.2`. It is a stabilization cut, not a feature expansion.

## Scope

`0.4.0-beta.2` promotes the alpha line after the following capabilities became deterministic and test-covered:

- `lai readiness` for environment and repository health.
- `lai release-check` for model-free release posture checks.
- `lai run export` for sanitized diagnostic bundles.
- `diagnose`, `ci-fix`, and `release` mode skills.
- Public CLI aliases for mode entrypoints such as `lai diagnose`, `lai ci-fix`, and `lai release`.

## Required local gate

Run these before tagging beta.2:

```bash
lai readiness
lai release-check --target 0.4.0-beta.2 --json
make check
make test-dev
make test
make validate
./scripts/install-local.sh
lai version
lai doctor
```

Expected release-check posture before tagging:

- `overall`: `ready`
- `phase`: `ready_to_tag`
- `expected_tag`: `v0.4.0-beta.2`
- `release_safety`: `true`

Expected posture after tagging and fast-forwarding main:

- `overall`: `ready`
- `phase`: `released`
- `exact_tag`: `v0.4.0-beta.2`

## Non-goals

The beta cut does not add autonomous Git release execution, package publication, model downloading, web search, cron execution, plugin loading, or a stronger shell sandbox. Those remain explicit future decisions.

## Remaining beta risks

- `bash` still runs with the user's OS permissions. The policy gateway reduces risk but is not a sandbox.
- Model-assisted modes remain constrained by the quality and context behavior of the configured local model.
- VS Code Chat Participant API compatibility can vary by VS Code build.
- Signed releases and provenance attestations are not yet implemented.

## Exit criteria

Beta.2 is acceptable when local validation, install smoke, `lai readiness`, `lai release-check`, and GitHub CI all pass for both `main` and the `v0.4.0-beta.2` tag.
