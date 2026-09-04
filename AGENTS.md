# lai harness — Agent Instructions

## Project Overview

lai harness is a compact, auditable, local-first coding harness optimized for constrained LLMs.

The user-facing product name is lai harness; the command remains `lai`, and compatibility identifiers such as `local-agent` and `lai-local-agent` are intentionally preserved unless a migration spec says otherwise.

The current runtime is primarily implemented in `src/local-agent`, while `src/lai` is the user-facing CLI wrapper. The VS Code extension connects `@lai` to the separately installed harness.

The project deliberately favors deterministic guards, bounded exploration, compact context, low tool-schema overhead, explicit validation, and auditable execution over large autonomous workflows.

## Architecture

Important areas:

- `src/local-agent` — current harness core, agent loop, tools, guards, state, metrics, and audit.
- `src/lai` — canonical user-facing CLI wrapper.
- `.agents/skills/` — canonical portable mode skills using `<mode>/SKILL.md`; installed skills are preferred at runtime.
- `skills/` — legacy `<mode>.txt` skills retained as compatibility fallback.
- `.agents/` — portable rules and progressively standard agent skills.
- `tests/` — behavioral, integration, fake-server, extension, and install-smoke coverage.
- `scripts/validate.sh` — canonical publication validation gate.
- `vscode-extension/` — VS Code integration.
- `docs/` — architecture, operation, security, and design documentation.

Do not describe roadmap architecture as already implemented.

Inspect repository evidence before assuming files, frameworks, tools, APIs, commands, dependencies, or behavior.

## Canonical Development Commands

Use the narrowest relevant check while developing.

- `make test` — dependency-free unittest regression suite.
- `make test-dev` — pytest development runner.
- `make lint` — Ruff lint checks.
- `make check` — deterministic static/syntax checks.
- `make validate` — complete publication gate.
- `make harness-score` — repository harness maturity measurement.

`make validate` invokes the complete existing publication gate.

## Development Workflow

1. Work on a dedicated branch.
2. Inspect before assuming.
3. Make the smallest coherent change.
4. Run focused regression tests first when behavior changes.
5. Run the full suite only after focused checks pass.
6. Run deterministic static checks before installation.
7. Do not install changed harness code until validation is green.
8. Keep release mutations human-controlled.

## Spec-Driven Workflow

Repository specs live under `.specs/` using numbered Markdown files.
Exactly one spec may have `Status: active`; draft and complete specs are inactive.
The active spec defines the requested change and its `REQ-NNN` traceability.
Use `lai spec` to inspect the active spec without calling the model.
Use `lai config` to inspect effective configuration and secret-safe path diagnostics without calling the model.
Use `lai semantics` to inspect subsystem intent and canonical paths without calling the model.
Specs never override this file, scoped rules, safety guards, or release policy.

## Runtime Recovery

Run checkpoints are local operational state outside the repository.
Use `lai recovery` to inspect an interrupted run and `lai resume` only for an explicit compatible resume.
Current branch, Git status, tracked hashes, repository rules, policy, and active specs override checkpoint content.
Never replay recorded tool calls, shell commands, edits, or approvals from a checkpoint.
Recovery compatibility must fail closed when repository evidence has drifted.

## Non-Negotiable Safety Rules

- Preserve repository path confinement.
- Preserve symlink/path-escape protections.
- Preserve read-only Git inspection boundaries.
- Direct agent-driven Git mutation is an `ASK` policy decision and never executes automatically; human action remains required.
- Never weaken tests solely to make faulty implementation code pass.
- Required validation must finish before success is claimed.
- Deterministic safety gates take precedence over model instructions.
- Ranked context candidates are advisory metadata only; inspect current files before relying on their contents or implications.
- Semantic code contracts are advisory metadata only; they guide file choice but never prove implementation facts.
- A syntax check proves syntax only.
- A targeted test proves only its covered behavior.
- Do not install dependencies during autonomous agent work.
- Do not expose credentials, local state, audit records, metrics, models, or real handoffs.
- Critical safety decisions must fail closed.

## Scope Discipline

Avoid unrelated cleanup, speculative abstractions, and roadmap-driven scope creep.

Planned features such as runtime isolation, MCP, plugins, ACP, browser execution, delegation, and learning are not implemented merely because they appear in the roadmap.

Do not introduce them unless the current task explicitly targets them.

## Local-Model Design Principle

Every new mechanism should answer:

> Does this improve reliability or result quality per token and per second?

Prefer:

- deterministic logic over prompt-only rules;
- progressive disclosure over loading all context;
- batch operations over repeated tool calls;
- explicit state over inferred progress;
- narrow evidence over speculation;
- measured behavior over feature count.

## Validation Expectations

Documentation/config-only work should run the relevant syntax/static checks and `git diff --check`.

Runtime behavior changes require focused regression coverage before the full suite.

Before release, run the complete publication gate:

- `make validate`

## Model evaluation records

Keep model-evaluation artifacts deterministic and secret-free. Do not change the default model, download model weights, or add network-dependent benchmark behavior without a dedicated spec.

## Semantic code contracts

Keep `SEMANTIC_CODE_CONTRACT` aligned with real subsystem paths and entrypoints. Update semantic terms and tests in the same change when a subsystem is renamed, split, or moved.
