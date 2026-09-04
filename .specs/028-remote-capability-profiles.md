# Spec: Remote capability profiles

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Expand authenticated asynchronous control runs to useful read-only `diagnose` and `release` workflows without exposing `bash` or any write-capable tool to a remote control child. Preserve local CLI behavior unchanged.

## Requirements

### REQ-001

Define an explicit remote/control-child tool profile instead of relying only on the normal local mode tool sets.

### REQ-002

Allow `diagnose` and `release` in `POST /v1/runs` while keeping `plan`, `review`, and `security` available.

### REQ-003

A control child for every allowed remote mode must receive no `bash`, write, package-install, OS-administration, or generic command-execution schema.

### REQ-004

Normal local `diagnose` and `release` invocations must retain their existing tool sets and behavior.

### REQ-005

Control-run status and lifecycle records must report the allowed modes and shell-free remote profile accurately.

### REQ-006

Add focused tests proving schema filtering happens before model calls and that rejected write-capable modes never spawn.

### REQ-007

Update security, control-plane, release, and public beta documentation without claiming complete shell containment.

## Acceptance Criteria

- Remote `diagnose` and `release` can complete against the fake model using only shell-free schemas.
- Captured chat-completion tool schemas for remote `diagnose` and `release` contain no `bash`, `edit`, `create`, `patch`, or `rewrite`.
- Local mode tests continue to show `bash` for local `diagnose` and `release` where currently expected.
- Full tests, Harness Score L4, publication scan, and release validation gates pass.

## Validation

- `REQ-001` / `REQ-003` / `REQ-006`: `PYTHONPATH=tests .venv/bin/python -m pytest -q tests/test_control_plane.py`.
- `REQ-002` / `REQ-005`: focused control API lifecycle and capability tests.
- `REQ-004`: local mode/tool-schema regression tests.
- `REQ-007`: `make lint`, `make check`, `make test-dev`, `make test`, `make harness-score-gate`, and `make validate`.

## Context and Constraints

Beta.12 is released at `v0.4.0-beta.12` and provides asynchronous remote `plan`, `review`, and `security` runs. Local `diagnose` and `release` currently include `bash`; the shell policy is intentionally not treated as a complete sandbox. The safer next increment is to narrow the remote schema rather than expose or parse arbitrary shell remotely.

## Non-Goals

- Do not expose `bash`, generic argv, environment, cwd, package installation, service management, or OS administration through HTTP.
- Do not enable `implement`, `fix`, `ci-fix`, `refactor`, `debug`, `test`, or general mode through HTTP.
- Do not add remote `ASK` approval objects or write-capable remote execution in this beta.
- Do not add Telegram, WhatsApp, Tailscale, PWA, or messaging credentials to the harness repository.
- Do not claim that the existing local `bash` tool is sandboxed.

## Implementation Notes

Keep the normal local tool map intact. Add a second explicit control-child capability map and intersect it with the local mode map only when the fixed internal control-child environment marker is present. Fail closed if a marked child requests a mode without a remote profile. The remote map must contain repository-inspection tools only.

## Traceability

- `REQ-001` / `REQ-003` / `REQ-004` / `REQ-006` -> `src/local-agent`, `tests/test_control_plane.py`, local tool-schema regression tests.
- `REQ-002` / `REQ-005` -> control API constants, status payload, scheduler records, and focused tests.
- `REQ-007` -> `docs/CONTROL-PLANE.md`, `docs/SECURITY-MODEL.md`, `README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `ROADMAP.md`, and release docs.
