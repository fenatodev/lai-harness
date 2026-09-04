# lai beta readiness

This document records the release posture for `0.4.0-beta.10`. It is a release-state convergence cut: model-assisted product behavior stays stable while local tag readiness and optional remote handoff evidence become consistent.

## Scope

`0.4.0-beta.10` adds:

- `lai project-handoff --remote` / `lai next-chat --remote` for opt-in live GitHub verification inside the handoff;
- separate local/offline and remote governance evidence in handoff JSON and Markdown;
- remote branch-protection, GitHub Release and VSIX digest evidence in the handoff without exposing credentials;
- `release-check` tag-target verification independent of the current HEAD tag description;
- `ready_for_integration` for clean feature-branch candidates;
- `ready_to_tag` only for clean synchronized `main` where `HEAD == origin/main` and the expected tag does not already point elsewhere;
- blocking behavior for divergent `main`, unavailable `origin/main`, or an expected tag that peels to another commit.

Harness Score remains gated at **L4 Self-correcting, 93/108 (86%)** using Harness Score 1.6.3.

## Required feature-branch gate

```bash
lai readiness
lai release-check --target 0.4.0-beta.10 --json
lai release-pack --target 0.4.0-beta.10 --with-vsix --json
lai project-handoff --target 0.4.0-beta.10 --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
./scripts/install-local.sh
lai version
```

Expected before merge: a clean feature branch reports `release-check.phase=ready_for_integration`, never `ready_to_tag`.

## Protected-main integration

1. Push `feature/v0.4.0-beta.10-release-state-convergence`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`, with the PR up to date.
4. Merge through GitHub without bypassing protection.
5. Fast-forward local `main` to `origin/main`.
6. Wait for merged-main CI and Harness Score L4 to succeed.
7. Run `lai release-check --target 0.4.0-beta.10 --json`; only then may the phase be `ready_to_tag`.

After the tag is pushed, wait for tag CI before creating the GitHub pre-release.

Final verification:

```bash
lai release-check --target 0.4.0-beta.10 --json
lai release-governance --target 0.4.0-beta.10 --remote --json
lai project-handoff --target 0.4.0-beta.10 --remote --json
```

Expected final posture: `release-check.phase=released`, remote governance `ready`, branch protection `ok`, GitHub Release `ok`, VSIX digest matching when attached, and no remaining `manual_actions` in the remote handoff.

## Non-goals

This cut does not add autonomous GitHub administration, network-dependent default commands, subagents, MCP, type checking, dependency locking, model downloading, or a stronger OS sandbox.

## Remaining beta risks

- Offline `release-check` proves local Git integration state, not GitHub Actions completion; CI remains a separate protected gate.
- Allowed `bash` still executes with the user's OS permissions; hooks and policy are guards, not containment.
- Model-assisted modes remain constrained by the configured local model.
- Signed releases and provenance attestations are not yet implemented.
