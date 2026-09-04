# Spec: run history browser

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Add deterministic commands that list and inspect local lai harness run history from existing metrics, audit, and checkpoint records without calling the model or replaying actions.

## Requirements

### REQ-001

`lai runs` must list recent local runs for the current repository with run IDs, mode, status, counters, policy counts, and tool counts.

### REQ-002

`lai run show <run-id>` must print a bounded summary for one recorded run.

### REQ-003

`lai run tail <run-id>` must print a bounded event timeline for one recorded run.

### REQ-004

Run history commands must be deterministic and must not call the model, start the model server, replay commands, or mutate repository files.

## Acceptance Criteria

- Installed `lai runs` works in a sample repository with no recorded runs.
- Synthetic JSONL records can be listed, shown, tailed, and emitted as JSON.
- Missing run IDs fail cleanly.
- Existing metrics, audit, recovery, and context behavior remains compatible.

## Validation

- `make check`
- `.venv/bin/python -m pytest -q`
- `python3 -m unittest discover -s tests -v`
- `make validate`

## Context and Constraints

Use the existing local JSONL metrics and audit files as the source of truth. Checkpoints may enrich the latest run, but history commands must remain useful even when no checkpoint exists.

## Non-Goals

- No replay of recorded tool calls.
- No browser UI.
- No database migration.
- No web/search feature.
- No automatic cleanup of historical logs beyond existing pruning behavior.

## Implementation Notes

Expose `lai runs`, `lai run show <run-id>`, and `lai run tail <run-id>`. Keep JSON output available for machine-readable inspection.

## Traceability

- `REQ-001` -> `test_run_history_lists_shows_and_tails_recorded_runs` and install smoke.
- `REQ-002` -> `test_run_history_lists_shows_and_tails_recorded_runs`.
- `REQ-003` -> `test_run_history_lists_shows_and_tails_recorded_runs`.
- `REQ-004` -> deterministic CLI subprocess tests and install smoke without server.
