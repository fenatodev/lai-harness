# Spec: Configuration and Server Workflow

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Make LAI configuration safer and easier to diagnose before model runtime by validating supported settings and exposing a deterministic, secret-safe configuration report.

## Requirements

### REQ-001

Configuration loading must reject unknown `[lai]` keys from `config.toml` with a clear error before any model or server interaction.

### REQ-002

Configuration values must be type-checked and normalized deterministically, including `host`, `port`, `model`, filesystem paths, `server_launcher`, `llama_server`, and `chat_template`.

### REQ-003

Invalid ports, empty required strings, URL/path-shaped hosts, NUL-containing values, and non-path filesystem values must fail closed with actionable messages.

### REQ-004

CLI flags must keep precedence over environment variables, which keep precedence over `[lai]` TOML values, which keep precedence over defaults.

### REQ-005

A deterministic `lai config` command must report effective configuration and path checks without starting, probing, or requiring the model server.

### REQ-006

Configuration diagnostics must never print API key contents or other secret file contents.

### REQ-007

Missing runtime directories or optional local files must degrade as diagnostics rather than blocking deterministic commands.

### REQ-008

The server workflow documentation must distinguish WSL/Windows launcher setup, Linux/native usage, and remote/local server configuration constraints.

### REQ-009

The implementation must remain standard-library-only and must not add sandboxing, approval UI, MCP, plugins, provider abstraction, model downloads, or secret material.

## Acceptance Criteria

- Invalid TOML keys and invalid value types fail before runtime.
- `lai config` works with the model server unavailable.
- `lai config` prints paths and statuses but not key contents.
- Existing `--show-config`, `lai doctor`, `lai context`, `lai recovery`, modes, policy, recovery, and publication gates remain green.
- WSL and non-WSL server setup expectations are documented.

## Validation

- `REQ-001`: unknown-key configuration tests.
- `REQ-002`, `REQ-003`: type, port, host, and path validation tests.
- `REQ-004`: precedence regression tests.
- `REQ-005`, `REQ-006`, `REQ-007`: deterministic `lai config` tests without server access.
- `REQ-008`: installation/troubleshooting documentation updates.
- `REQ-009`: full validation and publication scan.

## Context and Constraints

Alpha.10 added context ranking and left configuration validation and non-WSL server workflow as a near-term roadmap item. Current configuration parsing accepts many malformed values until later runtime boundaries. Alpha.11 should improve operator feedback without creating an OS sandbox or adding external dependencies.

## Non-Goals

- OS sandboxing, container execution, filesystem virtualization, or process isolation.
- Interactive approval UI or persistent approval grants.
- MCP, plugins, delegates, learning, or provider abstraction.
- Automatic model downloads, model redistribution, or bundled chat templates.
- Secret generation or printing.

## Implementation Notes

Prefer a small explicit schema over dynamic validation. Treat persisted config as untrusted input. Keep deterministic commands useful even when optional files are missing. Report secrets only by path and file status.

## Traceability

- `REQ-001` -> unknown-key tests
- `REQ-002` -> normalized value tests
- `REQ-003` -> invalid type/value tests
- `REQ-004` -> precedence regression test
- `REQ-005` -> deterministic CLI test
- `REQ-006` -> redaction test
- `REQ-007` -> missing path diagnostic behavior
- `REQ-008` -> docs updates
- `REQ-009` -> validation/publication gates
