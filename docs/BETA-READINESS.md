# lai beta readiness

This document records the release posture for `0.4.0-beta.12`. It is an asynchronous read-only control-run cut: authenticated loopback clients can invoke shell-free model analysis while the HTTP boundary still excludes repository writes, generic shell execution, and approval workflows.

## Scope

`0.4.0-beta.12` adds:

- `POST /v1/runs` for `plan`, `review`, and `security` only;
- one serialized model worker plus at most four queued requests;
- `GET /v1/runs/<control_run_id>` lifecycle/result inspection;
- scoped cancellation with `DELETE /v1/runs/<control_run_id>`;
- fixed subprocess argv/cwd with `shell=False`, dedicated process groups, no caller-controlled executable/environment/cwd fields, and no implicit model-service autostart;
- bounded stdout/stderr retention with truncation indicators;
- bounded in-memory terminal control-run retention;
- deterministic queue/cancellation tests and a real subprocess smoke against `FakeLlamaServer`.

Harness Score remains gated at **L4 Self-correcting** using Harness Score 1.6.3.

## Required feature-branch gate

```bash
lai control-token status --json
lai release-check --target 0.4.0-beta.12 --json
lai release-pack --target 0.4.0-beta.12 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: the tree is clean, spec 027 is complete, focused control-plane tests pass, the real fake-model subprocess smoke passes, and `release-check.phase=ready_for_integration` on the feature branch.

## Protected-main integration

1. Push `feature/v0.4.0-beta.12-async-readonly-control-runs`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the PR up to date.
4. Merge through GitHub without bypassing protection.
5. Fast-forward local `main` to `origin/main`.
6. Wait for merged-main CI and Harness Score L4 to succeed.
7. Run `lai release-check --target 0.4.0-beta.12 --json`; only then may the phase be `ready_to_tag`.
8. Push only the annotated beta.12 tag, wait for tag CI, then create the GitHub pre-release.

Final verification:

```bash
lai release-check --target 0.4.0-beta.12 --json
lai release-governance --target 0.4.0-beta.12 --remote --json
lai project-handoff --target 0.4.0-beta.12 --remote --json
```

Expected final posture: release-check `released`, remote governance `ready`, branch protection `ok`, GitHub Release `ok`, VSIX digest matching when attached, and `manual_actions=[]`.

## Non-goals

This cut does not add Telegram, WhatsApp, Tailscale, a PWA, remote writes, `ASK` approval objects, public binding, generic command execution, autonomous GitHub administration, or shell-capable `diagnose`/`release` runs over HTTP.

## Remaining beta risks

- The control API token protects the application surface, but OS-account compromise still defeats local process isolation.
- The `bash` tool is not a complete sandbox. `diagnose` and `release` therefore remain outside the mobile boundary until structured shell hardening is implemented.
- Model prompt injection remains possible inside the three read-only modes, although their tool schemas contain no shell or write tools.
- Tailscale/mobile transport is not enabled by this repository; it belongs behind a separate gateway/private-network layer.
- Explicit approval objects and write-capable remote operation still require a separate design.
