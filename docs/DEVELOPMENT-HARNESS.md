# Development harness

The repository development harness protects changes to LAI itself. It is distinct from the product autonomy presets proposed in the [project plan](PROJECT-PLAN-2026-09.md). Safe/Autonomous Sandbox/Full do not grant this development session permission to install dependencies, mutate Git or publish.

## Current commands and proportional feedback

Use the cheapest trustworthy check for the affected boundary, then stop when required evidence is complete. This documentation revision does not change Makefile, CI, runtime guards or required status checks.

| Change class | Local evidence | Broader evidence |
| --- | --- | --- |
| Documentation/config | Relevant parser, links/static checks and `git diff --check`; `make check` for Harness syntax/static | Normal CI; no repeated full runtime suite merely for prose |
| Small behavior correction | Focused regression for actual failure and relevant static/type/lint | Normal CI; broaden only for new risk/failure |
| Significant feature | Focused behavior/integration tests plus relevant main suite at coherent integration | CI verifies supported environments |
| Critical authority/credentials/sandbox/schema | Focused adversarial/integration and all boundary-relevant gates | Full gate before freezing the capability |
| Milestone/release freeze | `make milestone-gate` once for the final coherent state | Protected CI/tag/publication evidence as currently required |

Do not chain targets whose evidence is already included. `make milestone-gate` currently includes Ruff, pytest, Harness Score and `validate.sh`; validate includes unittest, strict mypy, syntax/static, publication scan and VSIX inspection. `lai validation matrix --json` exposes the implemented risk-proportional inventory: retained check IDs, cost tiers, failure fixtures, Python-floor rationale and the planned reduction from repeated broad gates during iteration to one full gate at milestone freeze. The matrix is metadata-only and does not execute checks, mutate remote settings or weaken required gates.

## Sensors and supported Python

`requirements-dev.in` is the human-maintained development-sensor manifest; `requirements.txt` is its generated pinned lock. Runtime installation does not consume these files and remains third-party-dependency-free. Future optional browser/MCP adapters require explicit specs and isolated provisioning, not implicit additions to the core.

The current `mypy.ini` strict ratchet covers seven files: both hooks and `src/lai_semantics.py`, `src/lai_config.py`, `src/lai_specs.py`, `src/lai_sessions.py`, `src/lai_web.py`. Expand it with tested subsystem extraction, not a monolith rewrite.

Python >=3.11 has a technical basis: `src/lai_config.py` uses stdlib `tomllib`. CI currently tests 3.11 and 3.12 on Ubuntu, running pytest, unittest, Ruff, mypy and static checks; the publication job repeats part through validate. The validation matrix keeps 3.11 as the floor, treats the current CI/dev runtime as the additional supported version only when tests pass, and coordinates required-check IDs with fixtures and release checks. Linux/WSL2 is the first product target; native Windows is later and is not proven by the existing model launcher.

## Policy-backed shell and feedback hooks

`.cursor/hooks/guard_shell.py` sends commands to `lai policy-check`, which reuses `evaluate_tool_policy` and reports `executed: false`. Mapping remains ALLOW→allow, ASK→explicit user action, DENY→block; unavailable/malformed policy evidence fails closed. Ordinary agent Git mutation remains ASK and selected destructive operations remain denied under current repository rules.

`.cursor/hooks/feedback_check.py` applies narrow syntax/lint/JSON/shell feedback after edits, never installs dependencies and remains best-effort. A successful hook is early feedback, not proof of behavioral correctness. `.agents/workflows/verify-change.md` remains the explicit development workflow.

## Maturity, CI and release boundaries

`harness-score` 1.6.4 is pinned and requires L4. It measures repository maturity, not sandbox security or operational autonomy. Do not add MCP/delegates/metadata merely to improve a score; their product contracts are A7/A9 of the new plan.

The current required-check set is `Python 3.11`, `Python 3.12`, `Publication gates`, `Harness Score L4`. `.github/workflows/ci.yml`, `harness-score.yml`, runtime release-governance expectations and tests must remain aligned. Remote protection changes are a separate authorized action, never a side effect of revising docs or shortening CI.

GitHub Actions use reviewed full-SHA pins with version comments; Dependabot changes remain reviewable. Publication setup-node uses Node 24 with package-manager caching disabled where unnecessary. No pin/dependency/runtime installation changes occur in this planning delivery.

## Validation evidence and stop rules

A syntax check proves syntax; a focused regression proves its covered behavior; milestone success requires its own done criteria. Record commands/results against the exact changed state, keep historic freeze evidence dated, and never describe prior CI as current proof. If gates are unavailable, report missing evidence rather than install dependencies autonomously or weaken checks. Freeze once the bounded deliverable is complete; future capabilities stay draft.
