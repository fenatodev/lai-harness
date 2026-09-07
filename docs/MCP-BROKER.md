# MCP broker foundation

`lai mcp` provides the first governed MCP boundary for lai harness. This milestone discovers and validates local MCP configuration without executing MCP tools.

```bash
lai mcp status
lai mcp --help
lai mcp status --help
lai mcp tools --help
lai mcp policy-check --help
lai mcp help
lai mcp status --json
lai mcp tools
lai mcp tools --json
lai mcp policy-check --operation status --json
lai mcp policy-check --operation list-tools --server desktop-commander --json
lai mcp policy-check --operation call-tool --server desktop-commander --tool read_file --json
```

## Config discovery

The broker checks these repository-local files:

- `.cursor/mcp.json`
- `.mcp.json`
- `.agents/mcp_config.json`

The supported server maps are `mcpServers` and `servers`.

## Safety boundary

- MCP tool execution is disabled in this foundation milestone.
- The commands are deterministic, local, model-free, and do not start MCP servers.
- Unknown `status` and `tools` flags fail closed with usage output instead of being silently ignored.
- Credential-shaped env keys such as `TOKEN`, `API_KEY`, `SECRET`, `PASSWORD`, and `AUTH` must use `${ENV_VAR}` interpolation in config files.
- The status payload lists env key names, never env values.
- Literal credential-shaped env values block the config and are not printed.

## Current policy

`status` and `list-tools` policy checks may be allowed because they are read-only and non-executing. `call-tool` is denied until an allowlisted execution broker is implemented under the same policy and audit boundary as the rest of the harness.

## Control plane routes

The same foundation is available through authenticated loopback control-plane routes:

- `GET /v1/mcp/status`
- `GET /v1/mcp/tools`
- `POST /v1/mcp/policy-check`

These routes preserve the same non-execution boundary as the CLI.

## Validation

The v0.4.5 local freeze gate is `make milestone-gate`. It covers Ruff, pytest, Harness Score L4, the publication/package gate, strict mypy, publication scanning, and VSIX inspection.
