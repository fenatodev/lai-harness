# 022 Project handoff

Status: complete
Mode: full

## Problem

Long ChatGPT sessions become slow and eventually hit context limits. lai harness needs a deterministic handoff artifact so a later chat can re-establish project state without relying on the previous conversation window.

## Requirements

- REQ-001: Provide a model-free CLI command that renders current project handoff context.
- REQ-002: Support JSON output for automation-friendly handoff metadata.
- REQ-003: Support writing handoff files outside the repository.
- REQ-004: Refuse writing handoff output inside the source repository.
- REQ-005: Include release-check, release-governance, branch/tag, safe workspace and manual action state.
- REQ-006: Add wrapper aliases suitable for user-facing next-chat workflows.
- REQ-007: Cover the command with unit and install smoke tests.

## Design

Add `lai project-handoff` and `lai next-chat` as deterministic commands backed by `--project-handoff`. The command reuses existing release-check, release-governance and safe-workspace collectors, then renders a Markdown summary and an optional JSON payload. With `--out`, it writes `PROJECT-HANDOFF.md`, `NEXT-CHAT-PROMPT.md`, and `summary.json` to an external directory.

## Validation

- `make check`
- focused project handoff tests
- isolated install smoke
- full pytest/unittest
- `make validate`
- installed command smoke
