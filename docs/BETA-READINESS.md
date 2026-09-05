# lai beta readiness

This document records the release posture for `0.4.0-beta.14`. It is the isolated-remote-work cut: the control plane adds write-capable agent modes only inside disposable safe workspaces and validates them through a fixed Docker sandbox.

## Scope

`0.4.0-beta.14` adds:

- remote `implement`, `fix`, `refactor`, and `ci-fix`;
- structured `validate` profiles instead of remote shell commands;
- per-run safe workspaces copied from tracked source contents;
- fixed no-network Docker validation with dropped capabilities and no host home/socket exposure;
- fail-closed sandbox readiness with no automatic image pull;
- bounded workspace status/changed-path/diff evidence in public run records;
- source-checkout immutability across remote work runs;
- updated private-mobile architecture documentation and version-coupled visual review.

Existing read-only modes remain shell-free and behaviorally compatible. Harness Score remains gated at **L4 Self-correcting** using Harness Score 1.6.3.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.14 --json
lai release-pack --target 0.4.0-beta.14 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 030 complete, tree clean after commit, focused sandbox/work-profile tests green, full validation green, visual review marker on beta.14, and `release-check.phase=ready_for_integration`.

## Protected-main integration

1. Push `feature/remote-work-profile`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the PR up to date.
4. Merge through GitHub without bypassing protection.
5. Fast-forward local `main` to `origin/main`.
6. Wait for merged-main CI and Harness Score L4 to succeed.
7. Run `lai release-check --target 0.4.0-beta.14 --json`; only then may the phase be `ready_to_tag`.
8. Generate/freeze the final main VSIX once, create/push only the annotated beta.14 tag, wait for tag CI, then create the GitHub pre-release with that exact asset.

Final verification:

```bash
lai release-check --target 0.4.0-beta.14 --json
lai release-governance --target 0.4.0-beta.14 --remote --json
lai project-handoff --target 0.4.0-beta.14 --remote --json
```

## Non-goals

This cut does not add direct source-checkout writes from HTTP, work-result promotion, approval execution, commit/push/merge/tag/publication, arbitrary remote shell, dependency installation, web search, browser automation, MCP/Desktop Commander, persistent chat sessions, public binding, or multi-user service isolation.

## Remaining beta risks

- Docker/container isolation is a meaningful boundary, not a proof against kernel/runtime escape or malicious mounted runtimes/dependencies.
- The local interactive `bash` tool remains unsandboxed; beta.14 keeps it out of every remote profile.
- Prompt injection/model mistakes can still create harmful or incorrect workspace changes; the source checkout is protected by isolation, not by assuming model correctness.
- Work diffs may contain sensitive content and must be treated according to repository sensitivity.
- Promotion/approval must bind to immutable work evidence before it is safe to apply remote results automatically.
- Messaging/mobile transport remains a separate gateway responsibility.
