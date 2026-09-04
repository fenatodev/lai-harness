# Spec: lai harness Branding

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Standardize the user-facing product identity as lai harness while preserving the established `lai` command and compatibility identifiers.

## Requirements

### REQ-001

User-facing documentation must consistently describe the product as lai harness.

### REQ-002

The primary CLI command must remain `lai`.

### REQ-003

Compatibility identifiers such as repository name, extension participant ID, publisher, and internal `local-agent` executable may remain unchanged when renaming them would break users.

### REQ-004

The version command must present the product as lai harness.

### REQ-005

The VS Code extension metadata must keep the visible name and configuration title aligned with lai harness.

### REQ-006

The change must include a small branding document that records canonical names and compatibility exceptions.

### REQ-007

Tests must protect the branding boundary so future changes do not accidentally rename the `lai` command or compatibility identifiers.

## Acceptance Criteria

- `lai version` reports lai harness with the alpha.12 version.
- `lai` remains the executable command installed by the local installer.
- The VS Code chat participant remains `@lai` and the participant ID remains compatible.
- No public documentation page presents the old product title `LAI — Local AI Agent`.
- Compatibility exceptions are documented explicitly.

## Validation

- `REQ-001`: documentation grep and test coverage for stale public title.
- `REQ-002`: install smoke verifies `lai` remains installed and usable.
- `REQ-003`: extension/package branding test verifies compatibility IDs are preserved.
- `REQ-004`: deterministic version CLI test.
- `REQ-005`: extension package metadata test.
- `REQ-006`: documentation presence check.
- `REQ-007`: unit and smoke tests.

## Context and Constraints

The command name `lai` is already short, useful, and present in examples. The internal `local-agent` executable, repository URL, extension participant ID, and publisher are compatibility identifiers. This milestone changes user-facing branding, not package topology.

## Non-Goals

- Renaming the repository.
- Renaming the `lai` command.
- Renaming the internal `local-agent` executable.
- Changing the VS Code participant ID.
- Adding model evaluation, web tools, sandbox execution, hooks, or approval grants.

## Implementation Notes

Use `lai harness` as the canonical product name. Use `lai` only for the CLI command or chat participant. Use `local-agent` only when referring to the internal executable path.

## Traceability

- `REQ-001` -> public documentation title and stale-name tests
- `REQ-002` -> install smoke test
- `REQ-003` -> extension compatibility metadata test
- `REQ-004` -> version CLI test
- `REQ-005` -> extension metadata test
- `REQ-006` -> `docs/BRANDING.md`
- `REQ-007` -> unit and smoke tests
