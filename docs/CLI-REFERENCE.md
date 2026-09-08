# CLI reference

The canonical command is `lai`. In a source checkout, use `./src/lai` before installation.

## Deterministic inspection commands

| Command | Description | Model required |
| --- | --- | --- |
| `lai --help` | Top-level help. | No |
| `lai --version` | Product version. | No |
| `lai status` | Workspace status. | No |
| `lai readiness` / `lai ready` | Repository/model/config readiness. | No |
| `lai config` | Effective config and path diagnostics without secrets. | No |
| `lai operating-mode` | Local-first development/release policy. | No |
| `lai gateway-contract --json` | Gateway compatibility contract. | No |
| `lai validation matrix [--json]` | Risk-proportional validation matrix. | No |
| `lai distribution status [--json]` | Installed-state and upgrade/uninstall policy. | No |

## Context commands

| Command | Description |
| --- | --- |
| `lai context map` | Metadata-only repository map. |
| `lai context changes` | Git status counts and path samples without raw diff. |
| `lai context diff` | Per-file numstat metadata. |
| `lai context checks` | Test/check inventory. |
| `lai context symbols <path>` | Bounded Python/JavaScript symbol metadata. |
| `lai context graph` | Python AST graph with advisory resolved/heuristic/unknown edges. |
| `lai context runs` | Metadata-only recent run history. |

## Model-backed modes

| Mode | Purpose |
| --- | --- |
| `lai plan` | Plan without file mutation. |
| `lai debug` | Diagnose a concrete failure. |
| `lai diagnose` | Operational diagnosis. |
| `lai review` | Review evidence. |
| `lai security` | Security-oriented review. |
| `lai release` | Release readiness reasoning. |
| `lai fix` / `lai ci-fix` | Targeted repair with validation. |
| `lai test` | Test-focused change. |
| `lai refactor` | Bounded refactor. |
| `lai implement` | Scoped implementation with validation. |

Model-backed modes still obey deterministic policy, budget, path confinement and validation guards.

## Control-plane commands

| Command | Description |
| --- | --- |
| `lai control-token init` | Create a separate control API token. |
| `lai serve --bind 127.0.0.1 --port 8765` | Start authenticated loopback control API. |
| `lai chat-bootstrap --control-url URL` | Local-chat readiness and optional first Safe chat. |
| `lai sessions ...` | List/show/delete repository-scoped sessions. |
| `lai runs ...` | Inspect local run history. |
| `lai recovery ...` | Inspect or clear recovery checkpoints. |
| `lai snapshot ...` | Inspect pre-write snapshot metadata. |
| `lai rollback ...` | Hash-checked rollback from captured snapshot. |

## External and fixture commands

| Command | Current boundary |
| --- | --- |
| `lai web search|fetch` | Bounded public GET evidence; untrusted. |
| `lai mcp status|tools|policy-check` | Diagnostics only through CLI; fixture execution is control-plane scoped. |
| `lai model eval|profile` | Deterministic model evaluation/profile helpers; no router or auto-switch. |
| `lai update ...` | Bounded update intelligence; no apply/install/download operation. |
| `lai release-check` | Local release readiness diagnostics. |
| `lai release-pack` | Local artifact preparation only; no tag/push/release. |

## Exit and safety notes

- `ASK` decisions require human action and are not replayed automatically.
- `DENY` decisions fail closed.
- Source checkout writes through the control plane are disabled; promotion is hash-bound.
- Real credentials, real browser profiles, real MCP servers and real external account actions are disabled unless a future spec implements them explicitly.
