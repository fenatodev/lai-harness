# Spec: lowercase identity and repository migration prep

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Standardize the public product identity as `lai harness` in lowercase and prepare a safe repository migration from `lai-local-agent` to `lai-harness` without breaking the `lai` command or current compatibility identifiers.

## Requirements

### REQ-001

Public product names in documentation, CLI deterministic headings, installer text, and VS Code display metadata must use `lai harness` in lowercase.

### REQ-002

The CLI command `lai`, configuration directories, `LAI_*` environment variables, and current compatibility identifiers must remain functional unless a later migration spec explicitly changes them.

### REQ-003

The release must document the intended GitHub repository slug `lai-harness` and the safe manual migration sequence for the remote repository, local folder, remotes, and links.

### REQ-004

The version must advance to `0.4.0-alpha.14` across CLI and VS Code extension metadata.

### REQ-005

Automated checks must prevent accidental regression to the uppercase public product spelling.

## Acceptance Criteria

- `lai version` reports `lai harness 0.4.0-alpha.14`.
- `lai model plan` and other deterministic headings use lowercase `lai` wording.
- VS Code extension display metadata uses `lai harness` while preserving command and participant compatibility.
- Repository migration documentation names `lai-harness` as the target slug and states what remains compatible.
- Tests pass without requiring a model server for deterministic commands.

## Validation

- `REQ-001`: run tests that scan public documentation and metadata for uppercase product spelling.
- `REQ-002`: run install smoke tests and extension compatibility tests.
- `REQ-003`: inspect `docs/REPOSITORY-MIGRATION.md`.
- `REQ-004`: run `lai version` and parse `vscode-extension/package.json`.
- `REQ-005`: run the public identity regression test.

## Context and Constraints

GitHub repository rename is a remote administrative action. This change prepares the repository and documentation, but does not force a remote rename from the local harness.

## Non-Goals

- Do not rename the `lai` command.
- Do not rename `local-agent`.
- Do not rename `~/.config/lai`, `~/.local/share/lai`, or `LAI_*` environment variables.
- Do not assume the GitHub repository has already been renamed.

## Implementation Notes

Use lowercase `lai harness` for the product. Use `lai` for the CLI command. Use `lai-harness` only for the intended repository slug. Preserve `lai-local-agent` only where it is an existing compatibility identifier or a pre-migration repository reference.

## Traceability

- `REQ-001` -> public identity scan and deterministic command tests.
- `REQ-002` -> install smoke and extension compatibility tests.
- `REQ-003` -> repository migration documentation.
- `REQ-004` -> version tests and package metadata checks.
- `REQ-005` -> regression scan test.
