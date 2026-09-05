# 021 — release governance

Status: complete
Workflow mode: implement

## Problem

The beta line can generate deterministic release checks and publication packs, but there is no single read-only command that explains which release work is complete and which GitHub-side actions remain manual.

## Goals

- Add a deterministic `lai release-governance` command.
- Provide JSON output for release operators.
- Keep the command read-only and model-free.
- Report local release-check posture, release-pack presence, and manual GitHub actions.
- Add `lai governance` as a concise alias.

## Non-goals

- Do not create tags.
- Do not merge or push branches.
- Do not upload VSIX files.
- Do not publish GitHub Releases.
- Do not attempt to administer GitHub branch-protection settings.

## Validation

- `make check`
- focused governance and install smoke tests
- full pytest and unittest suites
- `make validate`
- local install smoke
- `lai release-governance --target 0.4.0-beta.6 --json`
