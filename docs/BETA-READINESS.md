# lai beta readiness

This document records the release posture for `0.4.0-beta.13`. It is a remote-capability-profile cut: the control plane adds useful `diagnose` and `release` analysis while keeping the mobile boundary shell-free and write-free.

## Scope

`0.4.0-beta.13` adds:

- an explicit remote capability map separate from local mode tools;
- remote `diagnose` and `release` in addition to `plan`, `review`, and `security`;
- pre-inference tool-schema reduction for every control child;
- explicit `shell-free-read-only` profile reporting in status and run lifecycle records;
- focused tests that inspect fake-model request schemas and prove forbidden tools never cross the boundary;
- unchanged local `diagnose`/`release` behavior.

Harness Score remains gated at **L4 Self-correcting** using Harness Score 1.6.3.

## Required feature-branch gate

```bash
lai release-check --target 0.4.0-beta.13 --json
lai release-pack --target 0.4.0-beta.13 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: spec 028 complete, tree clean, focused remote-profile tests green, full validation green, and `release-check.phase=ready_for_integration`.

## Protected-main integration

1. Push `feature/v0.4.0-beta.13-remote-capability-profiles`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the PR up to date.
4. Merge through GitHub without bypassing protection.
5. Fast-forward local `main` to `origin/main`.
6. Wait for merged-main CI and Harness Score L4 to succeed.
7. Run `lai release-check --target 0.4.0-beta.13 --json`; only then may the phase be `ready_to_tag`.
8. Push only the annotated beta.13 tag, wait for tag CI, then create the GitHub pre-release.

Final verification:

```bash
lai release-check --target 0.4.0-beta.13 --json
lai release-governance --target 0.4.0-beta.13 --remote --json
lai project-handoff --target 0.4.0-beta.13 --remote --json
```

## Non-goals

This cut does not add Telegram, WhatsApp, Tailscale, a PWA, remote writes, `ASK` approval objects, public binding, caller-controlled commands, autonomous GitHub administration, or shell-capable remote execution.

## Remaining beta risks

- The local `bash` tool remains unsandboxed; beta.13 avoids exposing it remotely rather than claiming shell containment.
- Prompt injection remains possible, but remote modes cannot invoke schemas that are not present in their capability profile.
- OS-account compromise still defeats local process isolation.
- Messaging/mobile transport remains a separate gateway responsibility.
- Explicit approval objects and write-capable remote operation require a later trust-boundary design.
