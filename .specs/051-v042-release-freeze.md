# Spec: v0.4.2 gateway contract freeze

Status: complete
Mode: release

## Problem

The gateway contract manifest adds a documented public CLI command and authenticated control-plane endpoint. If merged without a release freeze, public `main` would describe behavior unavailable in the latest published release.

## Requirements

- REQ-001: Bump the canonical runtime and VS Code extension package version from `0.4.1` to `0.4.2`.
- REQ-002: Update current-release README/PT-BR, release governance, handoff, visual marker, changelog, and release notes to target `v0.4.2`.
- REQ-003: Preserve `v0.4.1` as historical release evidence rather than rewriting it away.
- REQ-004: Do not add new runtime features, gateway transport, messaging integrations, model switching, or release publication in this freeze spec.
- REQ-005: Validate with focused current-version/release tests and the full `make milestone-gate` before integration.

## Non-goals

- Do not publish the release from this spec commit.
- Do not create tag, release asset, PR merge, or remote branch-protection change locally.
- Do not implement `lai-gateway`, PWA, Telegram, Tailscale, OAuth, or notification delivery.

## Validation

- Focused freeze tests: `6 passed in 6.37s`.
- `release-check --target 0.4.2 --json` confirmed `version_target=ok`; dirty tree/spec active were the only expected local blockers before commit.
- Full freeze gate: `make milestone-gate` passed in `129.05s` with 273 pytest + 98 subtests, Harness Score L4 100/108, 273 unittest, strict mypy, publication scan, and VSIX inspection.
