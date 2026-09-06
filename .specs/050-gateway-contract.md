# Spec: Gateway contract manifest

Status: complete
Mode: diagnose

## Problem

`lai-gateway` is intentionally a separate companion project, but gateway clients still need a stable, machine-readable description of the harness control-plane contract. Today the companion would have to scrape docs or duplicate endpoint assumptions, which is fragile and invites unsafe drift.

## Requirements

- REQ-001: Expose a deterministic gateway contract payload from the harness without adding Telegram, PWA, Tailscale, notification, or messaging dependencies.
- REQ-002: The contract must describe supported control-plane endpoints, authentication expectations, request limits, run modes, session limits, and explicit forbidden capabilities.
- REQ-003: Expose the same payload through an authenticated `GET /v1/gateway-contract` endpoint and a deterministic local CLI command.
- REQ-004: The payload must not include bearer tokens, model API keys, secret file contents, host environment variables, or private session/run transcripts.
- REQ-005: Preserve the existing loopback-only control-plane boundary and do not add remote shell, source checkout write, commit, push, merge, tag, release, browser automation, or direct llama.cpp proxy authority.
- REQ-006: Add focused tests for CLI payload shape, endpoint authentication, endpoint payload equality, and install wrapper routing.

## Non-goals

- Do not implement `lai-gateway` inside this repository.
- Do not add Telegram, PWA, WhatsApp, Tailscale, OAuth, webhook, or notification delivery code.
- Do not change release version, branch protection, or publication flow in this spec.

## Validation

- Focused CLI/endpoint/install tests: `3 passed in 6.72s`.
- Affected suites: `171 passed, 68 subtests passed in 36.69s`.
- HTTP dogfood: unauthenticated `/v1/gateway-contract` returned `401`; authenticated returned `200`, schema version `1`, 14 routes, no secret words.
- Full milestone gate: `make milestone-gate` passed in `130.52s` with 273 pytest + 98 subtests, Harness Score L4 100/108, 273 unittest, strict mypy, publication scan, and VSIX inspection.
