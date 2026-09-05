# Beta readiness

This document records the release posture for `0.4.0-beta.16`. It is a reproducible-quality-sensors hardening cut: runtime capabilities stay stable while development/CI sensors become version-locked and static type checking becomes an enforced ratchet.

## Scope

`0.4.0-beta.16` adds:

- `requirements-dev.in` as the small human-maintained development-sensor manifest;
- generated `requirements.txt` with exact direct and transitive sensor versions;
- pinned mypy 2.3.1 with a strict initial scope over the Python guardrail hooks;
- explicit hook annotations without weakening fail-closed policy or repository confinement;
- canonical `make typecheck` and type checking in both Python CI jobs;
- type checking inside the complete publication gate;
- CI installation from the canonical generated lock rather than an independently maintained sensor list;
- documentation cleanup for the already-released beta.15 promotion boundary.

The product runtime remains Python-standard-library-only. Harness Score is gated at **L4 Self-correcting** and now measures **100/108 (93%)** with Harness Score 1.6.3.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.16 --json
lai release-pack --target 0.4.0-beta.16 --with-vsix --json
make typecheck
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 032 complete, generated lock committed, strict mypy green on its declared scope, hook regressions green, full tests/publication gates green, visual review marker on beta.16, Harness Score at least L4 with no maturity regression, and `release-check.phase=ready_for_integration`.

## Protected-main integration

1. Push `feature/v0.4.0-beta.16-reproducible-quality-sensors`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the PR up to date.
4. Merge through GitHub without bypassing protection.
5. Fast-forward local `main` to `origin/main`.
6. Wait for merged-main CI and Harness Score L4 to succeed.
7. Run `lai release-check --target 0.4.0-beta.16 --json`; only then may the phase be `ready_to_tag`.
8. Generate/freeze the final main VSIX once, create/push only the annotated beta.16 tag, wait for tag CI, then create the GitHub pre-release with that exact asset.

Final verification:

```bash
lai release-check --target 0.4.0-beta.16 --json
lai release-governance --target 0.4.0-beta.16 --remote --json
lai project-handoff --target 0.4.0-beta.16 --remote --json
```

## Non-goals

This cut does not add MCP/Desktop Commander integration, custom subagents, delegation/orchestration, persistent remote sessions, web/browser tools, generic remote shell, commit/push/PR automation, protected-branch writes, runtime Python dependencies, or model downloads.

## Remaining beta risks

- The strict type-check boundary covers the typed Python guardrail modules, not the monolithic extensionless `src/local-agent` runtime yet.
- Expanding type coverage should follow subsystem extraction rather than forcing broad annotations into the current monolith.
- Version locking improves reproducibility but does not replace dependency provenance/signature verification.
- Docker/container and local `bash` security boundaries are unchanged from beta.15.
- Commit, push, PR creation, merge, and protected-main integration remain separate governed actions after promotion.
