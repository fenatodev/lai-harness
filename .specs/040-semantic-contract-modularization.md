# Spec: semantic contract modularization

## Metadata
- Mode: `full`
- Status: `complete`
- Target: `0.4.0-beta.24`

## Goal
Start the post-beta.23 monolith reduction with a low-risk deterministic subsystem: move semantic code-contract data and matching helpers out of `src/local-agent`, preserve behavior and installation, and expand the strict mypy ratchet to the extracted module.

## Context and Constraints
- `src/local-agent` is currently a 13k+ line standard-library-only runtime.
- The roadmap explicitly calls for extending semantic code contracts and strict type checking as subsystems split out.
- This cut must not change policy, model execution, network authority, remote capabilities, or release authority.
- Local installation must remain dependency-free and work through the existing `lai` / `local-agent` scripts.

## Requirements
### REQ-001
**Typed semantic module**
Create a dedicated standard-library-only semantic-contract module with explicit typed structures for subsystem metadata and the public contract.

### REQ-002
**Behavior preservation**
`lai semantics` / `--json` and semantic context-ranking reasons must remain deterministic and behaviorally compatible.

### REQ-003
**Canonical navigation update**
The semantic contract must identify the extracted module as a canonical path so future model navigation follows the new boundary instead of assuming all runtime semantics live in `src/local-agent`.

### REQ-004
**Installed-runtime compatibility**
`scripts/install-local.sh` must install the extracted module beside the runtime entrypoint without adding Python package installation or external runtime dependencies.

### REQ-005
**Strict type-check ratchet**
Add the extracted semantic module to the existing strict mypy scope while preserving the current hook guardrails.

### REQ-006
**Regression coverage**
Add focused source-tree, installed-runtime, semantic-ranking, and quality-sensor regressions that fail if the module is omitted, the contract drifts, or the mypy ratchet shrinks.

### REQ-007
**Release alignment**
Advance product/extension/public release metadata to `0.4.0-beta.24` and document this cut as structural hardening, not new authority.

## Acceptance Criteria
- `src/local-agent` imports and re-exports semantic helpers from a dedicated module.
- deterministic semantics output and semantic ranking tests stay green without a model server.
- an isolated local install includes the module and `lai semantics` works from that install.
- `mypy --strict` includes the extracted module and passes.
- no new third-party runtime dependency is introduced.
- full project publication gates pass before this spec becomes complete.

## Validation
- `REQ-001`: inspect `src/lai_semantics.py` and run strict mypy on the configured scope.
- `REQ-002`: run deterministic semantics CLI/JSON and semantic context-ranking regressions.
- `REQ-003`: assert semantic JSON exposes `src/lai_semantics.py` as a canonical path.
- `REQ-004`: run install smoke in an isolated temporary bin/data directory and execute installed `lai semantics`.
- `REQ-005`: run `make typecheck` and quality-sensor coverage that requires the new module in the strict file set.
- `REQ-006`: run focused semantic, install-smoke, and quality-sensor regressions.
- `REQ-007`: run version/publication metadata checks and full publication gates.
- Full gates: `make lint`, `make typecheck`, `make check`, `make test-dev`, `make test`, `make harness-score-gate`, `make validate`.

## Non-Goals
- Do not split policy, control-plane, update-intelligence, or release-governance code in the same cut.
- Do not change model selection or run a model bake-off in this cut.
- Do not add MCP, web tools, browser actions, generic remote shell, or Git publication authority.
- Do not redesign packaging around pip/setuptools.

## Implementation Notes
- Extract only semantic contract data/rendering/matching in this cut; leave broader context ranking in the monolith.
- Keep the extracted module importable both from source-tree `importlib` tests and from the installed bin directory.
- Treat the strict mypy file list as a monotonic ratchet: existing typed hooks remain required and the new module is additive.
- Update semantic canonical paths to make future extractions discoverable by the same contract.

## Traceability
- `REQ-001` -> `src/lai_semantics.py` typed contract structures and mypy.
- `REQ-002` -> `src/local-agent` compatibility wrappers and semantic/context regressions.
- `REQ-003` -> semantic subsystem metadata and JSON contract assertions.
- `REQ-004` -> `scripts/install-local.sh` and install smoke coverage.
- `REQ-005` -> `mypy.ini` and `tests/test_quality_sensors.py`.
- `REQ-006` -> semantic, install-smoke, and quality-sensor test suites.
- `REQ-007` -> runtime/VS Code metadata, roadmap/changelog/release readiness documentation.

## Validation Evidence

- Extracted deterministic semantic contract/runtime helpers into `src/lai_semantics.py`; `src/local-agent` reduced from 13,616 to 13,411 lines while preserving compatibility wrappers.
- `lai semantics --json` reports `0.4.0-beta.24` and canonical `semantic-code-contracts` paths led by `src/lai_semantics.py`.
- Isolated install smoke confirms `lai_semantics.py` is installed beside `local-agent` and installed deterministic commands remain functional.
- Strict mypy scope now covers three source files: both existing guardrail hooks plus `src/lai_semantics.py`; `mypy --strict` passes.
- Full pytest after implementation: 249 passed + 85 subtests.
- Full dependency-free unittest suite: 249 passed.
- Ruff, compile/static checks, publication scan, and VSIX packaging/inspection are green.
- Harness Score 1.6.4 remains L4 Self-correcting at 100/108 (93%); no score-only subagent or MCP work was added.
- Full `make validate` completed successfully with `All lai harness publication gates passed.`
