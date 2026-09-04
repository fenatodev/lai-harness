# Spec: run detail polish

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Make run-history inspection faster for real work by adding latest-run shortcuts and clearer validation/failure summaries without calling the model or replaying actions.

## Requirements

### REQ-001

`lai run last` and `lai run show --last` must show the most recent recorded run for the current repository.

### REQ-002

`lai run tail --last` must tail the most recent recorded run while preserving bounded output and `--limit` validation.

### REQ-003

`lai run show` must include a validation timeline with command, status, and bounded result text when validation events exist.

### REQ-004

`lai run show` JSON must expose `last_validation`, `validation_events`, and `last_failure` fields for machine-readable triage.

### REQ-005

Run detail polish must remain deterministic and must not call the model, start the model server, replay commands, or mutate repository files.

## Acceptance Criteria

- Synthetic JSONL records can be listed, shown, tailed, and resolved through `--last`.
- Validation pass/fail status is summarized in text and JSON.
- Missing run IDs and empty latest-run lookups fail cleanly.
- Installed `lai runs` still works in a sample repository with no recorded runs.

## Validation

- `make check`
- `.venv/bin/python -m pytest -q`
- `python3 -m unittest discover -s tests -v`
- `make validate`

## Context and Constraints

Use existing local metrics, audit, and checkpoint records only. Historical records are advisory operational evidence, not current-file evidence.

## Non-Goals

- No replay of recorded tool calls.
- No browser UI.
- No database migration.
- No web/search feature.
- No interactive approval grants.

## Implementation Notes

Extend the existing run-history command surface instead of adding a new storage format. Keep result snippets bounded to avoid leaking large logs into normal CLI output.

## Traceability

- `REQ-001` -> `test_run_history_lists_shows_and_tails_recorded_runs`.
- `REQ-002` -> `test_run_history_lists_shows_and_tails_recorded_runs`.
- `REQ-003` -> `test_run_history_lists_shows_and_tails_recorded_runs`.
- `REQ-004` -> `test_run_history_lists_shows_and_tails_recorded_runs`.
- `REQ-005` -> deterministic CLI subprocess tests and install smoke without server.
