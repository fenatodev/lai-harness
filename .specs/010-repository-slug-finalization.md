# Spec: repository slug finalization

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Finalize the public repository migration from `fenatodev/lai-local-agent` to `fenatodev/lai-harness` after the GitHub rename, without breaking the `lai` command or existing compatibility identifiers.

## Requirements

### REQ-001

Public clone URLs and repository metadata must point to `fenatodev/lai-harness`.

### REQ-002

The repository migration documentation must describe the completed remote rename and the optional local folder rename.

### REQ-003

Compatibility identifiers must remain unchanged unless a later migration spec explicitly changes them.

### REQ-004

The version must advance to `0.4.0-alpha.16` across CLI and VS Code extension metadata.

### REQ-005

Tests must guard the new public repository URL while preserving compatibility identifiers.

## Acceptance Criteria

- `lai version` reports `lai harness 0.4.0-alpha.16`.
- `README.md` and `README.pt-BR.md` clone from `https://github.com/fenatodev/lai-harness.git`.
- VS Code extension package repository metadata points to `https://github.com/fenatodev/lai-harness.git`.
- Compatibility identifiers such as `local-agent`, `lai-chat`, and `lai-local-agent.lai` remain intact.
- Deterministic commands still run without contacting the model server.

## Validation

- `REQ-001`: run tests that assert public repository URLs use `fenatodev/lai-harness`.
- `REQ-002`: inspect `docs/REPOSITORY-MIGRATION.md`.
- `REQ-003`: run extension compatibility and branding tests.
- `REQ-004`: run version tests and parse `vscode-extension/package.json`.
- `REQ-005`: run the full validation gate.

## Context and Constraints

The GitHub repository rename is a remote administrative action and has already been performed by the user. This change only finalizes repository references in code and documentation.

## Non-Goals

- Do not rename the `lai` command.
- Do not rename `local-agent`.
- Do not rename `~/.config/lai`, `~/.local/share/lai`, or `LAI_*` environment variables.
- Do not rename the VS Code participant ID.
- Do not rename the local working directory inside this change.

## Implementation Notes

Use `lai-harness` for public repository links. Preserve `lai-local-agent` where it is an existing extension namespace, participant ID, artifact name, historical migration source, or compatibility identifier.

## Traceability

- `REQ-001` -> README and package repository URL checks.
- `REQ-002` -> repository migration documentation.
- `REQ-003` -> extension compatibility tests.
- `REQ-004` -> version tests and package metadata checks.
- `REQ-005` -> publication validation gate.

