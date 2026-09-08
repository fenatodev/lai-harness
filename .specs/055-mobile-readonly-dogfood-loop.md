# Spec: mobile read-only dogfood loop

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Prove that the Gateway phone path can support real read-only LAI project work without expanding authority.

The milestone should turn mobile access from an operator health panel into a repeatable dogfood loop for safe planning, review, and status inspection.

## Requirements

### REQ-001

Define two or three named mobile dogfood scenarios that use existing Harness read-only capabilities.

### REQ-002

Document the expected session lifecycle for pair, mobile session, control session, expiry, reuse, and cleanup.

### REQ-003

Keep all phone-triggered runs read-only and shell-free. The phone path must not expose write modes, commit, push, release, browser action, model management, or MCP tool execution.

### REQ-004

Make sanitized event inspection sufficient for a phone user to understand progress without reading stdout, stderr, raw transcripts, task text, file contents, or private paths.

### REQ-005

Capture dogfood failures as Harness or Gateway fixtures before adding new mobile controls.

### REQ-006

Update Gateway documentation only where a real operator action changes.

## Acceptance Criteria

- A phone user can inspect health, pair, create or select a session, run a read-only task, inspect sanitized status/events, and recover from expiry.
- Expired pair or session state produces bounded, actionable guidance without printing secrets.
- Every mobile route involved remains protected in private mode.
- No route broadens Harness authority beyond the existing contract.
- Focused tests and a real dogfood run pass.

## Validation

- `REQ-001`: Focused documentation or fixture check proving the named dogfood scenarios are declared.
- `REQ-002`: Focused lifecycle test or documented state transition check for pair, session, expiry, reuse, and cleanup.
- `REQ-003`: Focused Gateway route/mode rejection tests proving phone-triggered runs remain read-only and shell-free.
- `REQ-004`: Focused run-event display or payload tests proving progress is sanitized and metadata-only.
- `REQ-005`: Dogfood evidence file or fixture records every observed failure before adding controls.
- `REQ-006`: Documentation diff is limited to real operator action changes.
- Repository gates: `make check` in every touched repository, Gateway/Harness stack compatibility check, and real mobile or local-private dogfood with secret-shape scan.

## Context and Constraints

Gateway currently exposes health, status, sessions, runs, sanitized events, model status, Telegram delivery, and MCP foundation visibility. This spec should use those capabilities before requesting new ones.

## Non-Goals

- Write-capable mobile runs.
- Mobile commit, push, PR, tag, or release actions.
- MCP tool execution.
- Browser automation.
- Automatic recurring notifications without explicit scheduling.

## Implementation Notes

Start with dogfood scripts and docs. Add UI only for repeated friction observed during the dogfood loop.

## Traceability

- `REQ-001` -> named dogfood scenarios and run records.
- `REQ-002` -> session lifecycle documentation/tests.
- `REQ-003` -> route/mode rejection tests.
- `REQ-004` -> sanitized event display tests.
- `REQ-005` -> fixtures created from observed failures.
- `REQ-006` -> focused documentation diff.

## Completion Evidence

Implemented in `lai-gateway` PR #42.

Evidence:

- Gateway session, run, and run-event payloads are sanitized for mobile read-only use.
- `scripts/mobile-readonly-dogfood.sh` proves the loop with write-mode rejection, session create/get/delete, read-only run creation, terminal polling, metadata-only event inspection, and secret-shape scanning.
- Gateway focused tests covered script, client, CLI, HTTP routes, private mode, and sanitization.
- Gateway `make check` and `make milestone-gate` passed with 209 tests and stack compatibility.
- Live local-private Gateway-to-Harness dogfood completed with sanitized output and no token-shaped content.

Cross-repo details live in the Gateway docs:

- `docs/MOBILE_READONLY_DOGFOOD.md`
- `docs/MOBILE_READONLY_DOGFOOD_EVIDENCE.md`
