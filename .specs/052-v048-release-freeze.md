# Spec: v0.4.8 context intelligence freeze

Status: complete
Mode: release

## Problem

The v0.4.8 branch adds user-visible context-intelligence commands and an operating-mode policy. Leaving that work in `Unreleased` while the runtime still reports `0.4.7` creates avoidable drift for local operators and the companion Gateway.

## Requirements

- REQ-001: Bump the canonical runtime and VS Code extension package version from `0.4.7` to `0.4.8`.
- REQ-002: Update current-release README/PT-BR, visual review metadata, changelog, and release notes to target `v0.4.8`.
- REQ-003: Preserve `v0.4.7` as historical release evidence rather than rewriting it away.
- REQ-004: Do not add new runtime features, Gateway transport, Telegram/PWA integration, model switching, MCP execution, or release publication in this freeze spec.
- REQ-005: Validate with focused current-version/context/release tests and the full `make milestone-gate` before integration.

## Non-goals

- Do not publish the release from this spec.
- Do not create a tag, release asset, PR merge, push, or remote branch-protection change locally.
- Do not implement `lai-gateway`, PWA, Telegram, Tailscale, OAuth, notifications, or model-provider switching.

## Validation

- Focused version/context/release tests passed: `33 passed, 137 deselected, 5 subtests passed in 3.10s`.
- `lai release-check --target 0.4.8 --json` confirmed `version_target=ok`, `release_channel=stable`, `expected_prerelease=false`, and `expected_tag=v0.4.8`; dirty tree was the expected local freeze blocker before commit.
- Full milestone gate passed in 167.65s: Ruff green, `311 pytest tests + 144 subtests`, Harness Score L4 `100/108`, `311 unittest tests`, strict mypy over seven files, publication scan clean, and VSIX inspection passed.
- Gateway stack compatibility passed from `lai-gateway` 0.1.34 against this checkout: Harness `0.4.8 >= 0.4.6`, contract compatibility ok, MCP foundation non-executing, and `overall=ready_for_local_commit`.
- No push, PR, tag, GitHub Release, Gateway transport, Telegram/PWA integration, model switching, MCP execution, or publication mutation occurred.
