# Spec: Run Export Bundle

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Add a deterministic command that exports one recorded lai run into a sanitized local diagnostic bundle.

## Requirements

### REQ-001

Provide `lai run export <run-id|--last>` and `lai run export <run-id|--last> --json`.

### REQ-002

Write a local bundle containing `summary.json`, `timeline.jsonl`, and `report.md`.

### REQ-003

Default exports must go under `$LAI_DATA_DIR/exports/` and support `--out DIR` for explicit destinations.

### REQ-004

Exported events must be sanitized and allowlisted; raw prompts, full tool arguments, full tool outputs, API keys, and unbounded logs must not be copied.

### REQ-005

The command must be deterministic and must not call the model, start the server, replay tools, or mutate repository files by default.

## Acceptance Criteria

- `lai run export --last` creates the three expected files for a recorded run.
- `lai run export --last --json` emits parseable JSON describing the bundle.
- Missing run IDs fail with the existing clean run-history error.
- Tests cover sanitization so raw arguments and prompt-like fields are absent from the exported timeline.

## Validation

- `REQ-001`: `python3 -m unittest tests.test_local_agent.LocalAgentTest.test_run_history_lists_shows_tails_and_exports_recorded_runs`
- `REQ-002`: same focused test checks files exist.
- `REQ-003`: same focused test uses `--out`.
- `REQ-004`: same focused test checks sanitized timeline contents.
- `REQ-005`: deterministic CLI test plus install smoke.

## Context and Constraints

The existing run history browser already folds metrics, audit events, and checkpoint state. Export should reuse that path instead of adding a database or replay mechanism.

## Non-Goals

- No remote upload.
- No automatic zip archive.
- No raw log dump.
- No action replay.

## Implementation Notes

The bundle is intentionally a directory, not an archive, to keep the alpha simple and inspectable with standard tools.

## Traceability

- `REQ-001` -> `handle_run_history`, `render_run_history_export`
- `REQ-002` -> `write_run_history_export`
- `REQ-003` -> `parse_run_history_out_dir`
- `REQ-004` -> `sanitize_run_history_export_event`
- `REQ-005` -> deterministic tests and docs
