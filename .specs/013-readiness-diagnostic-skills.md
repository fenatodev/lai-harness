# Spec: readiness and diagnostic skills

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Add an operational readiness command and focused diagnostic/release-oriented skills that improve pre-beta reliability without expanding autonomous power.

## Requirements

### REQ-001

`lai readiness` and `lai ready` must report repository, Git, server authentication, path, skill, recovery, and latest-run readiness without calling the model or mutating files.

### REQ-002

Readiness must support JSON output for deterministic inspection.

### REQ-003

Add standard and legacy skills for `diagnose`, `ci-fix`, and `release`.

### REQ-004

The new skills must be available through the CLI, installed skill tree, and VS Code chat participant commands.

### REQ-005

`diagnose` and `release` must remain read-only; `ci-fix` may write but must retain validation guards and release-sensitive Git operations must remain human-gated.

## Acceptance Criteria

- `lai readiness` and `lai readiness --json` run without model inference.
- `lai ready` aliases readiness through the public wrapper.
- New mode skills load from standard `SKILL.md` files.
- Installed smoke verifies the new skills and readiness command.
- Full validation remains green.

## Validation

- `make check`
- `.venv/bin/python -m pytest -q`
- `python3 -m unittest discover -s tests -v`
- `make validate`

## Context and Constraints

Keep the change pre-beta focused. Do not add web search, cron, plugin execution, sandboxing, automatic model downloads, or automatic release mutation.

## Non-Goals

- No automatic tag, merge, push, or package publication.
- No model call inside readiness.
- No new database for readiness state.
- No autonomous background monitoring.

## Implementation Notes

Readiness should reuse existing config, doctor, recovery, run history, and skill parsing functions where possible. Warnings should be visible but not require a non-zero exit.

## Traceability

- `REQ-001` -> readiness CLI and wrapper smoke tests.
- `REQ-002` -> readiness JSON tests.
- `REQ-003` -> standard skill loading tests and install smoke.
- `REQ-004` -> VS Code package/extension command tests and install smoke.
- `REQ-005` -> tool policy tests and validation guard mode coverage.
