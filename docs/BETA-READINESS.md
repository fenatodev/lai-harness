# Beta readiness

This document records the release posture for `0.4.0-beta.15`. It is the approved-workspace-promotion cut: remote work remains isolated, while a successful result can cross into a durable feature worktree only through an exact SHA-256-bound approval and deterministic revalidation.

## Scope

`0.4.0-beta.15` adds:

- read-only `GET /v1/runs/<id>/promotion` proposals for successful isolated work runs;
- exact complete-patch SHA-256 binding rather than approval of the bounded display diff;
- immutable source baseline captured by the control server before model execution;
- NUL-delimited structured changed-path inventory and the first-path parsing fix found during mobile dogfooding;
- source SHA/branch/clean-state and mutable-workspace-metadata drift checks;
- repeated `full` validation in the existing no-network Docker sandbox immediately before promotion;
- deterministic `lai/promotion-<run-id>` Git branch/worktree creation under the LAI data directory;
- `git apply --check` followed by exact apply and post-apply patch-hash verification;
- idempotent same-hash promotion and fail-closed conflicting approval;
- no edit or branch switch of the active source checkout.

Existing remote work/read-only modes remain compatible. Harness Score remains gated at **L4 Self-correcting** using Harness Score 1.6.3.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.15 --json
lai release-pack --target 0.4.0-beta.15 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 031 complete, tree clean after commit, focused promotion/control-plane tests green, real Docker+Git promotion smoke green, full validation green, visual review marker on beta.15, and `release-check.phase=ready_for_integration`.

## Protected-main integration

1. Push `feature/v0.4.0-beta.15-approved-promotion`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the PR up to date.
4. Merge through GitHub without bypassing protection.
5. Fast-forward local `main` to `origin/main`.
6. Wait for merged-main CI and Harness Score L4 to succeed.
7. Run `lai release-check --target 0.4.0-beta.15 --json`; only then may the phase be `ready_to_tag`.
8. Generate/freeze the final main VSIX once, create/push only the annotated beta.15 tag, wait for tag CI, then create the GitHub pre-release with that exact asset.

Final verification:

```bash
lai release-check --target 0.4.0-beta.15 --json
lai release-governance --target 0.4.0-beta.15 --remote --json
lai project-handoff --target 0.4.0-beta.15 --remote --json
```

## Non-goals

This cut does not add commit, push, PR creation, merge, tag/release publication, arbitrary remote shell, dependency installation, direct active-checkout writes, web search, browser automation, MCP/Desktop Commander, persistent chat sessions, public binding, or multi-user service isolation. Gateway approval UI/Telegram buttons are a separate companion cut after the core endpoint is released.

## Remaining beta risks

- Docker/container isolation is a meaningful boundary, not proof against kernel/runtime escape or malicious mounted runtimes/dependencies.
- The local interactive `bash` tool remains unsandboxed and absent from every remote profile.
- Model mistakes may produce broad or incorrect safe-workspace patches; only `succeeded` runs with a valid proposal can promote, and humans/gateways must review the proposal before approval.
- Promotion creates a local feature worktree with uncommitted changes. Git commit/push/PR governance is intentionally still separate.
- Work/promotion diffs may contain sensitive content and must be handled according to repository sensitivity.
- Messaging/mobile identity and approval UX remain a separate gateway responsibility.
