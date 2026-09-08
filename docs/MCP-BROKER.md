# MCP broker foundation

For the public status vocabulary used across docs, see [Documentation portal](README.md#status-vocabulary).


`lai mcp` provides the implemented MCP foundation in lai harness v0.4.9. It discovers and validates local MCP configuration without executing generic MCP tools. A narrow `fixture_stdio` execution adapter is available only through authenticated control-plane routes for deterministic local fixtures; repository MCP config alone still does not start servers. Real private servers, HTTP transports, OAuth, sampling/callbacks, and wildcard tool trust remain planned work.

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

`lai mcp tools` summarizes declared servers from these files. It does not connect to servers or perform protocol-level tool discovery. An env interpolation declaration is configuration hygiene, not credential isolation or approval to start a process.

## Safety boundary

- Generic MCP tool execution is disabled in the CLI and in `POST /v1/mcp/policy-check`.
- The CLI commands are deterministic, local, model-free, and do not start MCP servers.
- The only executable adapter is `fixture_stdio` through `POST /v1/mcp/execution/call`, and it requires exact server-config and tool-schema hashes from `GET /v1/mcp/execution/status`.
- `fixture_stdio` runs under the verified sandbox executor, uses a minimal environment, disables network through the sandbox profile, and writes only bounded text artifacts under `artifacts/` in a disposable MCP workspace outside the source checkout.
- Unknown `status` and `tools` flags fail closed with usage output instead of being silently ignored.
- Credential-shaped env keys such as `TOKEN`, `API_KEY`, `SECRET`, `PASSWORD`, and `AUTH` must use `${ENV_VAR}` interpolation in config files.
- The status payload lists env key names, never env values.
- Literal credential-shaped env values block the config and are not printed.

## Current policy

`status` and `list-tools` policy checks may be allowed because they are read-only and non-executing. Generic `call-tool` remains denied. The fixture execution route is not a policy-check replay path; it is a separate hash-bound test adapter with bounded startup/call/output behavior and terminal `outcome_unknown` on timeout.

The planned broker will execute real tools under the harness policy boundary. Safe will use narrow allowlists and explicit approvals where needed; Autonomous Sandbox will allow authorized operations inside its verified boundary; Full / Trusted will use explicit host scopes. Server startup, transport, tool arguments, external effects, credentials, cancellation, and aggregate budgets must all be governed. Tool descriptions and server claims of read-only behavior remain untrusted. This replaces indefinite non-execution as a product destination without weakening the present v1 contract.

## Control plane routes

The same foundation is available through authenticated loopback control-plane routes:

- `GET /v1/mcp/status`
- `GET /v1/mcp/tools`
- `POST /v1/mcp/policy-check`
- `GET /v1/mcp/execution/status`
- `POST /v1/mcp/execution/call`

The first three routes preserve the same non-execution boundary as the CLI. The execution routes expose only the deterministic `fixture_stdio` adapter; they do not trust repository config to install or start arbitrary servers.

## Historical validation

The v0.4.5 foundation used the `make milestone-gate` freeze gate, covering Ruff, pytest, Harness Score L4, the publication/package gate, strict mypy, publication scanning, and VSIX inspection. This is historical foundation evidence, not proof of an executable broker.

Additional local dogfood used a temporary repository-local `.cursor/mcp.json` with env interpolation. It verified config discovery, non-executing status/tool summaries, allowed `list-tools` policy classification, denied `call-tool`, and no printing of literal secret values or interpolation expressions. No real repository MCP config is checked in.
