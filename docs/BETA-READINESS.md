# lai beta readiness

This document records the release posture for `0.4.0-beta.11`. It is a local-control-plane foundation cut: the harness gains an authenticated loopback HTTP surface for future mobile gateways without exposing model execution, shell execution, or repository writes over HTTP.

## Scope

`0.4.0-beta.11` adds:

- `lai control-token init|status` with a control-plane secret separate from the llama.cpp API key;
- secure token creation with cryptographic randomness, mode `0600`, no default secret output, and explicit overwrite only;
- `lai serve` backed only by the Python standard library;
- loopback-only binding with public/LAN/tailnet bind addresses rejected in this beta;
- bearer-authenticated JSON endpoints for status, readiness, run-history summaries, and policy classification;
- request-size/media-type/malformed-JSON handling and JSON method/error responses;
- an explicit HTTP capability boundary: no model execution, shell execution, or repository writes;
- installed-wrapper smoke coverage for token initialization and authenticated `/v1/status`.

Harness Score remains gated at **L4 Self-correcting** using Harness Score 1.6.3.

## Required feature-branch gate

```bash
lai control-token status --json
lai release-check --target 0.4.0-beta.11 --json
lai release-pack --target 0.4.0-beta.11 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected before merge: the tree is clean, the spec is complete, focused control-plane tests pass, the installed smoke can start the local API, and `release-check.phase=ready_for_integration` on the feature branch.

## Protected-main integration

1. Push `feature/v0.4.0-beta.11-local-control-plane`.
2. Open a PR into protected `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the PR up to date.
4. Merge through GitHub without bypassing protection.
5. Fast-forward local `main` to `origin/main`.
6. Wait for merged-main CI and Harness Score L4 to succeed.
7. Run `lai release-check --target 0.4.0-beta.11 --json`; only then may the phase be `ready_to_tag`.
8. Push only the annotated beta.11 tag, wait for tag CI, then create the GitHub pre-release.

Final verification:

```bash
lai release-check --target 0.4.0-beta.11 --json
lai release-governance --target 0.4.0-beta.11 --remote --json
lai project-handoff --target 0.4.0-beta.11 --remote --json
```

Expected final posture: release-check `released`, remote governance `ready`, branch protection `ok`, GitHub Release `ok`, VSIX digest matching when attached, and `manual_actions=[]`.

## Non-goals

This cut does not add Telegram, WhatsApp, Tailscale, a PWA, remote model runs, remote writes, approval workflows, public binding, autonomous GitHub administration, or a generic HTTP command endpoint.

## Remaining beta risks

- The control API token protects the application surface, but OS account compromise still defeats local process isolation.
- Tailscale/mobile exposure is not enabled by this repository; it will live behind a separate gateway/private-network layer.
- `GET /v1/readiness` can probe the configured llama.cpp server but does not invoke model generation.
- Asynchronous agent runs and remote `ASK` approvals still require a separate design before mobile write-capable operation is safe.
