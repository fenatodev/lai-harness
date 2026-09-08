# lai harness documentation

This is the documentation portal for the current `lai harness` repository. It separates current, implemented behavior from planning records and historical release material.

## Start here

| Need | Canonical document |
| --- | --- |
| First local run | [Quick start](QUICKSTART.md) |
| Install or uninstall | [Installation](INSTALLATION.md) and [Distribution](DISTRIBUTION.md) |
| Configure model/API paths | [Configuration](CONFIGURATION.md) |
| Understand the system | [Architecture](ARCHITECTURE.md) and [Diagrams](DIAGRAMS.md) |
| Use the CLI | [CLI reference](CLI-REFERENCE.md) |
| Understand modes | [Operating modes](MODES.md) |
| Understand control APIs | [Control plane](CONTROL-PLANE.md) and [Gateway contract](GATEWAY-CONTRACT.md) |
| Understand safety boundaries | [Security model](SECURITY-MODEL.md), [Threat model](AUTONOMY-THREAT-MODEL.md), [Authority and approvals](AUTHORITY-APPROVALS.md), [Sandbox](SANDBOX.md), [Safe workspaces](SAFE-WORKSPACES.md) |
| Understand execution records | [Runtime records](RUNTIME-RECORDS.md), [Observability](OBSERVABILITY.md), [Recovery](RECOVERY.md) |
| Contribute | [Development harness](DEVELOPMENT-HARNESS.md), [Testing and validation](TESTING-VALIDATION.md), [Contributing](../CONTRIBUTING.md) |
| See roadmap status | [Roadmap](../ROADMAP.md), [Known limitations](KNOWN-LIMITATIONS.md), [FAQ](FAQ.md) |

## Capability documentation

| Area | Document |
| --- | --- |
| Runtime execution model | [Runtime execution](RUNTIME-EXECUTION.md) |
| Context intelligence and Python code graph | [Context intelligence](CONTEXT-INTELLIGENCE.md) |
| Model capability profiles | [Model capabilities](MODEL-CAPABILITIES.md) and [Model evaluation](MODEL-EVALUATION.md) |
| Skills | [Skills](SKILLS.md) |
| MCP fixture execution | [MCP broker](MCP-BROKER.md) |
| Web evidence, egress and browser fixture | [Web evidence](WEB-EVIDENCE.md) |
| Sessions, forks and delegates | [Sessions, forks and delegates](SESSIONS-FORKS-DELEGATES.md) |
| Distribution, upgrades and uninstall | [Distribution](DISTRIBUTION.md) |
| Troubleshooting | [Troubleshooting](TROUBLESHOOTING.md) |
| Repository presentation | [Project presentation](PROJECT-PRESENTATION.md) |
| GitHub metadata | [Repository graduation notes](GITHUB-REPOSITORY-GRADUATION.md) |

## Current vs historical documents

The following documents are current operational references and should describe implemented behavior only:

- `README.md`, `README.pt-BR.md`
- `docs/README.md`
- `ARCHITECTURE.md`, `INSTALLATION.md`, `CONFIGURATION.md`, `CLI-REFERENCE.md`, `MODES.md`
- `CONTROL-PLANE.md`, `GATEWAY-CONTRACT.md`, `SECURITY-MODEL.md`, `SAFE-WORKSPACES.md`, `SANDBOX.md`
- `RUNTIME-EXECUTION.md`, `RUNTIME-RECORDS.md`, `OBSERVABILITY.md`, `RECOVERY.md`
- `DEVELOPMENT-HARNESS.md`, `TESTING-VALIDATION.md`, `TROUBLESHOOTING.md`, `KNOWN-LIMITATIONS.md`, `FAQ.md`

The following are historical or planning records. They are useful for traceability, but they must not be read as current capability claims unless they are reconciled by the current docs and tests:

- `PROJECT-PLAN-2026-09.md`
- `EXECUTION-BACKLOG-2026-09.md`
- `PLANNING-MANIFEST-2026-09.json`
- `DECISION-LOG-2026-09.md`
- `RISK-REGISTER-2026-09.md`
- `REPLAN-COVERAGE-2026-09.md`
- `M1-*`, `M3-*`, `M4-*`, release notes and older handoff documents

## Status vocabulary

- **Implemented**: exists in checked-in code and has tests or deterministic CLI/API evidence.
- **Fixture-only**: exists as a bounded local fixture for contract testing, not a real external integration.
- **Experimental**: planned in draft specs and intentionally excluded from normal public capability claims.
- **Planned/deferred**: not currently implemented.
- **Out of scope**: explicitly not provided by `lai harness`.
