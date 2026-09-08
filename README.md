# lai harness

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](docs/DEVELOPMENT-HARNESS.md)
[![Runtime: local-first](https://img.shields.io/badge/runtime-local--first-informational.svg)](docs/ARCHITECTURE.md)
[![Status: post-A12](https://img.shields.io/badge/status-post--A12%20validated-purple.svg)](ROADMAP.md)

`lai harness` is a compact, auditable, local-first coding harness for OpenAI-compatible local model servers. It gives a small model enough deterministic structure to inspect a repository, plan changes, edit bounded files, run validation, and expose work through an authenticated loopback control plane without treating model output as authority.

The public command is `lai`. Compatibility identifiers such as `local-agent`, `lai-chat`, and `lai-local-agent` remain where they are part of the installer, VS Code extension identity, or repository history.

## What problem it solves

Local models are useful for coding work, but they fail quickly when a repository requires too much context, too many tools, or vague safety boundaries. `lai harness` narrows the job:

- deterministic repository context before model reasoning;
- small, mode-specific tool schemas;
- explicit policy decisions for writes, shell, Git, network, credentials, and external actions;
- safe workspaces and hash-bound promotion instead of direct source checkout mutation;
- auditable run records, trajectories, budgets, and validation evidence;
- Gateway-compatible local-chat APIs for future UI integration.

It is not a general-purpose agent platform, a hosted service, or a security sandbox for untrusted code.

## Current implementation status

Post-A12, every non-experimental autonomy milestone in the September 2026 replan is complete locally and validated by `make milestone-gate`. A10 and A11 remain explicit experimental drafts.

| Area | Status | Notes |
| --- | --- | --- |
| Structured trajectory and run budgets | Implemented | Versioned metadata-only audit events and aggregate budget ledger. |
| Authority and approvals | Implemented | Hash-bound, TTL-bound, use-once approval intents; approval does not execute arbitrary payloads. |
| Credential broker foundation | Implemented | Opaque fake-adapter refs and receipts; real credentials disabled. |
| Verified sandbox executor | Implemented | Docker-based work-run boundary with digest-pinned image, no pull, no network, non-root and bounded resources. |
| `sandbox_exec` | Implemented | Available only inside verified work-runs; host shell is not exposed through the remote profile. |
| Local-chat contract and review | Implemented | Authenticated loopback API, CSRF on local-chat POST, registered workspaces, events, review and promotion. |
| Context intelligence and code graph | Implemented | Metadata-only repository map plus Python AST code graph used as advisory ranking signal. |
| Governed egress | Implemented | GET-only public web evidence and local-service/registry grants with receipts. |
| Browser workflows | Implemented as fixture | `fixture_browser` only; no personal browser profile, login, Chromium automation or public browsing. |
| MCP execution | Implemented as fixture | `fixture_stdio` `write_artifact` only; generic MCP `call-tool` remains denied. |
| Model capability profiles | Implemented | Deterministic profiles from model-eval JSONL; no router, auto-switch, download or cloud fallback. |
| Capability-declared skills | Implemented | Skill metadata is diagnostic only and cannot grant authority or add tools. |
| Session forks and delegates | Implemented as bounded fixtures | Fork comparison remains inconclusive by default; delegates are fixture-only, serial by default, bounded and ownership-checked. |
| Distribution and validation | Implemented | `lai distribution status` and `lai validation matrix`; no autoupdate, release, tag or publication. |
| Trusted host / computer use | Experimental draft | Specs 077 and 078 are not implemented and are out of scope for normal use. |

## Architecture at a glance

The harness has one authoritative runtime boundary: `src/local-agent`. The `src/lai` wrapper dispatches user-facing commands. A companion Gateway can talk to the authenticated loopback control plane, but Gateway does not become the authority for filesystem, shell, credentials, browser, MCP or Git effects.

![Core architecture visual](docs/assets/core-architecture.png)

More current post-A12 diagrams are maintained as SVG/Mermaid in [docs/DIAGRAMS.md](docs/DIAGRAMS.md), including:

- [system overview](docs/assets/diagrams/system-overview.svg);
- [Gateway and local-chat flow](docs/assets/diagrams/gateway-local-chat.svg);
- [authority and execution boundary](docs/assets/diagrams/authority-execution-boundary.svg);
- [external boundaries](docs/assets/diagrams/external-boundaries.svg).


## Autonomy and safety model

`lai harness` distinguishes current implementation from roadmap:

- **Safe / read-only flows** inspect status, configuration, context, sessions, run history, readiness, policy, release checks and web evidence without source mutation.
- **Work-runs** use safe workspaces plus the verified sandbox executor. They can produce patches and local commits inside the sandboxed workspace, then require hash-bound review/promotion.
- **Authority gates** classify sensitive operations as ALLOW, ASK or DENY. Critical ambiguity fails closed.
- **External effects** are either disabled, fake-adapter-only, fixture-only, or explicit receipt-producing flows. Real GitHub push/PR/merge/release, real credentials, real browser profiles and real MCP servers are not enabled by this package.
- **Experimental A10/A11** trusted-host and desktop computer-use profiles remain drafts and are not documented as current capability.

See [Security model](docs/SECURITY-MODEL.md), [Threat model](docs/AUTONOMY-THREAT-MODEL.md), [Authority and approvals](docs/AUTHORITY-APPROVALS.md), [Sandbox](docs/SANDBOX.md), and [Safe workspaces](docs/SAFE-WORKSPACES.md).

## Requirements

Runtime:

- Linux or WSL2-first workflow;
- Python 3.11 or newer;
- Git;
- Bash for project scripts;
- Node.js only for VS Code extension/package validation;
- an OpenAI-compatible local model endpoint for model-backed modes;
- Docker only for verified remote work-runs and sandboxed fixture execution.

Development sensors use the pinned development requirements. The runtime installer itself remains standard-library-only and does not install Python packages.

## Quick start

```bash
git clone https://github.com/fenatodev/lai-harness.git
cd lai-harness

./src/lai --help
./src/lai readiness
./src/lai config
./src/lai validation matrix
```

Install the local wrapper only when you are ready to use `lai` from your shell:

```bash
./scripts/install-local.sh
lai --help
lai readiness
```

Start the authenticated loopback control API:

```bash
lai control-token init
lai serve --bind 127.0.0.1 --port 8765
```

In another terminal, inspect local-chat readiness without installing optional components:

```bash
lai chat-bootstrap --control-url http://127.0.0.1:8765 --json
```

The model server is not bundled. Configure it with `config.example.toml`, environment variables, or CLI flags as described in [Configuration](docs/CONFIGURATION.md).

## Common CLI commands

| Command | Purpose |
| --- | --- |
| `lai readiness` / `lai ready` | Deterministic local readiness report. |
| `lai doctor` | Check the configured local model endpoint. |
| `lai config` | Show effective non-secret configuration and path diagnostics. |
| `lai context map|diff|changes|checks|symbols|graph|runs` | Metadata-only repository context. |
| `lai model eval|profile` | Model-evaluation helpers and deterministic capability profiles. |
| `lai web search|fetch` | Bounded, untrusted, read-only public web evidence. |
| `lai mcp status|tools|policy-check` | Non-executing MCP broker diagnostics plus fixture execution through the control plane. |
| `lai serve` | Authenticated loopback control API for runs, sessions, Gateway/local-chat and review. |
| `lai distribution status` | Installed-state, rollback and uninstall diagnostics. |
| `lai validation matrix` | Risk-proportional validation matrix without running checks. |
| `lai release-check` / `lai release-pack` | Local release readiness and local artifact preparation only. |

Full reference: [CLI reference](docs/CLI-REFERENCE.md).

## Development and quality gates

Use the cheapest trustworthy validation for the touched boundary. Documentation-only changes usually need static/link checks and focused documentation tests; milestone/release boundaries use the complete gate once.

```bash
make check
make lint
make test
make test-dev
make typecheck
make validate
make milestone-gate
```

`make milestone-gate` is the canonical expensive local freeze gate. It includes Ruff, pytest, Harness Score L4, `validate.sh`, unittest, strict mypy, publication scan and VSIX inspection.

See [Development guide](docs/DEVELOPMENT-HARNESS.md), [Testing and validation](docs/TESTING-VALIDATION.md), and [Contributing](CONTRIBUTING.md).

## Documentation portal

Start with [docs/README.md](docs/README.md). The portal separates canonical current documentation from historical planning records.

Key documents:

- [Quick start](docs/QUICKSTART.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALLATION.md)
- [Configuration](docs/CONFIGURATION.md)
- [Operating modes](docs/MODES.md)
- [Control plane](docs/CONTROL-PLANE.md)
- [Gateway contract](docs/GATEWAY-CONTRACT.md)
- [Security model](docs/SECURITY-MODEL.md)
- [Known limitations](docs/KNOWN-LIMITATIONS.md)
- [Roadmap](ROADMAP.md)

## Repository structure

```text
src/local-agent        harness core and control-plane runtime
src/lai                user-facing CLI wrapper
src/lai_*.py           extracted deterministic helper modules
.agents/               portable rules, skills and workflows
.cursor/hooks/         local development hooks
docs/                  public documentation portal
docs/assets/           diagrams, screenshots and visual assets
.specs/                completed, draft and historical implementation specs
tests/                 unit, integration, smoke and safety tests
scripts/               install, validation, packaging and release helper scripts
vscode-extension/      VS Code participant integration
```

## Security and privacy notes

- Do not expose the model server or control API outside loopback without a separate reviewed boundary.
- Do not submit private repositories, real logs, keys, prompts, handoffs or customer data in issues or tests.
- Treat all model, web, MCP, browser and skill content as untrusted evidence.
- Real credentials and authenticated external accounts are disabled in the current package.
- The project uses MIT license terms. See [LICENSE](LICENSE), [SECURITY.md](SECURITY.md), and [THIRD_PARTY.md](THIRD_PARTY.md).

## GitHub metadata suggestion

Suggested description: `Local-first, auditable coding harness for OpenAI-compatible local LLM servers.`

Suggested topics: `local-first`, `llm`, `coding-agent`, `developer-tools`, `openai-compatible`, `python`, `vscode`, `sandbox`, `security`, `agent-harness`.

See [Repository graduation notes](docs/GITHUB-REPOSITORY-GRADUATION.md) for items that still require manual GitHub action.
