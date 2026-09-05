# Beta readiness

This document records the release posture for `0.4.0-beta.19`. This is a release-metadata correctness cut; LAI runtime capability, model behavior, persistence formats, and repository authority remain unchanged.

## Scope

`0.4.0-beta.19`:

- selects release notes from the exact target-version level-2 section;
- bounds that selection at the next level-2 heading;
- generates `release-body.md` from that target section instead of a legacy marker;
- derives the annotated-tag message from the same target heading;
- keeps a neutral fallback when target-specific notes are absent;
- adds regressions for stale older markers and version-prefix collisions;
- aligns current release documentation with the actual beta scope.

This cut addresses a real publication defect observed while closing beta.18: the generated body still described beta.16 and the generated tag title still described an older capability cut.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.19 --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 035 complete, focused release-pack regressions green, generated title/body matching beta.19, full Python 3.11/3.12 and publication gates green, and `release-check.phase=ready_for_integration`.

## Protected-main integration

1. Push `feature/v0.4.0-beta.19-release-notes-correctness`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`.
4. Merge without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and wait for merged-main CI.
6. Require `lai release-check --target 0.4.0-beta.19 --json` to report `ready_to_tag` before tagging.
7. Freeze the final VSIX from merged `main`, push only `v0.4.0-beta.19`, wait for tag CI, then publish the pre-release with that exact asset.

## Non-goals

No MCP, subagents, persistent sessions, web/browser tools, remote shell, model-provider changes, runtime dependencies, Git authority, or control-plane capability is added.

## Remaining beta risks

- If target-specific release notes are absent, the pack intentionally falls back to a neutral generic body/title; operators must treat that as a signal to review release metadata before publication.
- Release publication remains an explicit human/authorized action after CI; this cut does not add automatic publishing authority.
- Runtime/session roadmap items remain separate cuts.