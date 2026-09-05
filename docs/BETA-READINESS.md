# Beta readiness

This document records the release posture for `0.4.0-beta.18`. This is a CI/supply-chain hardening cut; LAI runtime capability, model behavior, and repository authority remain unchanged.

## Scope

`0.4.0-beta.18` adds:

- Node 24-compatible GitHub-maintained actions at reviewed releases;
- immutable full-SHA pins for `actions/checkout`, `actions/setup-python`, and `actions/setup-node`;
- Node.js 24 as the explicit publication packaging runtime;
- disabled setup-node package-manager caching because publication validation does not require an npm dependency cache;
- weekly Dependabot review PRs for GitHub Actions dependencies;
- regression tests that fail if official actions drift back to floating tags or legacy action runtimes.

This cut does not chase Harness Score points. Its purpose is to remove a live GitHub Actions deprecation warning and make CI dependencies easier to audit and reproduce.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.18 --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 033 complete, action-hardening regressions green, all workflow actions pinned as reviewed, full Python 3.11/3.12 and publication gates green, and `release-check.phase=ready_for_integration`.

## Protected-main integration

1. Push `feature/v0.4.0-beta.18-actions-supply-chain`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`.
4. Merge without bypassing branch protection.
5. Fast-forward local `main` to `origin/main`.
6. Wait for merged-main CI and Harness maturity to succeed.
7. Run `lai release-check --target 0.4.0-beta.18 --json`; only `ready_to_tag` may proceed to a tag.
8. Freeze the final VSIX from merged `main`, push only `v0.4.0-beta.18`, wait for tag CI, then publish the pre-release with that exact asset.

## Non-goals

This cut does not add MCP, subagents, sessions, web/browser tools, remote shell, model-provider changes, runtime Python dependencies, commit/push/PR authority, or new control-plane endpoints.

## Remaining beta risks

- GitHub-hosted runners satisfy the Node 24 action runtime requirement; self-hosted runner support would need an explicit minimum-runner policy before adoption.
- Full-SHA pinning improves reproducibility but still depends on GitHub-hosted action source and review of Dependabot updates.
- The VS Code extension still requires an active VS Code/WSL IPC context for normal CLI installation.
- Runtime/session/state roadmap items remain separate cuts.
