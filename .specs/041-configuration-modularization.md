# Spec: configuration modularization

## Metadata
- Mode: `full`
- Status: `complete`
- Target: `0.4.0 stabilization milestone`

## Goal
Continue incremental monolith reduction by moving deterministic configuration parsing, validation, path diagnostics, and status rendering into a typed standard-library-only module while preserving source-tree and installed-runtime behavior.

## Context and Constraints
- `src/local-agent` remains a 13k+ line runtime after the semantic-contract extraction.
- Configuration resolution is deterministic and already covered across CLI, environment, TOML, XDG defaults, control-plane setup, and runtime-record tests.
- The published version must remain `0.4.0-beta.24` during this internal stabilization spec; release metadata is prepared only at the milestone boundary.
- The extracted module must remain standard-library-only and install beside `local-agent` without pip/setuptools.

## Requirements
### REQ-001
**Typed configuration module**
Create `src/lai_config.py` containing configuration constants, validation, normalization, precedence resolution, path diagnostics, and status rendering with strict type coverage.

### REQ-002
**Behavioral compatibility**
Preserve CLI > environment > TOML > defaults precedence, XDG paths, validation failures, secret-safe status output, and existing public helper names exposed by `src/local-agent`.

### REQ-003
**Installed-runtime compatibility**
Install `lai_config.py` beside `local-agent` and prove that installed deterministic `lai config` behavior works without a model server or Python package manager.

### REQ-004
**Semantic navigation**
Update the configuration semantic contract so `src/lai_config.py` is the canonical first path while retaining the compatibility entrypoint in `src/local-agent`.

### REQ-005
**Strict type-check ratchet**
Add `src/lai_config.py` to the strict mypy scope without shrinking any existing typed file coverage.

### REQ-006
**Regression coverage**
Add or strengthen focused tests covering direct module behavior, compatibility re-exports, isolated installation, semantic navigation, and the type-check ratchet.

### REQ-007
**Milestone cadence preservation**
Do not change public version, release notes, tag, release checklist, VSIX version, or GitHub publication state for this internal spec.

## Acceptance Criteria
- `src/local-agent` no longer owns the configuration implementation body and imports/re-exports the stable helpers from `src/lai_config.py`.
- Existing configuration and runtime-record tests pass unchanged or with only loader/install assertions required by modularization.
- Installed `lai config` remains deterministic and secret-safe.
- `mypy --strict` passes with the new module included.
- no third-party runtime dependency or new operational authority is introduced.
- focused checks and the full local regression/publication gate pass before the spec becomes complete.

## Validation
- `REQ-001`: inspect `src/lai_config.py` and run `make typecheck`.
- `REQ-002`: run configuration, control-plane configuration, and runtime-record precedence/validation regressions.
- `REQ-003`: run isolated install smoke and execute installed `lai config` without a server.
- `REQ-004`: assert semantic JSON places `src/lai_config.py` first for the configuration subsystem.
- `REQ-005`: run the quality-sensor ratchet regression and strict mypy.
- `REQ-006`: run focused config/install/semantic/quality tests, then the full local suite.
- `REQ-007`: assert runtime/extension/public release metadata remains `0.4.0-beta.24` and no release mutation occurs.
- Full local milestone gate: `make lint`, `make typecheck`, `make check`, `make test-dev`, `make test`, `make harness-score-gate`, `make validate`.

## Non-Goals
- Do not change configuration keys, precedence, defaults, or secret handling semantics.
- Do not change the default model.
- Do not extract policy, control plane, update intelligence, release governance, or spec workflow in this spec.
- Do not add package-manager installation, MCP, web/browser tools, remote shell, or Git authority.
- Do not bump to beta.25 or publish a GitHub release for this spec alone.

## Implementation Notes
- Keep compatibility imports in `src/local-agent` so existing tests and internal callers continue to resolve `load_configuration`, `path_status`, and `render_config_status`.
- Pass product version into the extracted status renderer rather than creating a second version source of truth.
- Keep default-model ownership in the configuration module and re-export it from the runtime.
- Treat the strict mypy file list as a monotonic ratchet.

## Traceability
- `REQ-001` -> `src/lai_config.py` and `mypy.ini`.
- `REQ-002` -> `src/local-agent` compatibility imports plus configuration/control/runtime-record tests.
- `REQ-003` -> `scripts/install-local.sh` and `tests/test_install_smoke.py`.
- `REQ-004` -> `src/lai_semantics.py` and semantic regressions.
- `REQ-005` -> `mypy.ini` and `tests/test_quality_sensors.py`.
- `REQ-006` -> focused and full regression suites.
- `REQ-007` -> unchanged public version/release metadata and clean local-only Git state.


## Validation Evidence

- Extracted configuration constants, validation, normalization, precedence resolution, path diagnostics, and rendering into typed `src/lai_config.py`; `src/local-agent` decreased from 13,411 to 13,090 lines.
- Differential comparison against the beta.24 runtime matched exactly across defaults, CLI/environment/TOML precedence, XDG/data paths, float-to-int legacy behavior, and representative invalid-key/port/host failures.
- Compatibility re-exports preserve `agent.load_configuration`, `agent.path_status`, and `agent.DEFAULT_MODEL`; deterministic config CLI behavior remains model-free and secret-safe.
- Isolated install smoke confirms `lai_config.py` is installed beside `local-agent` and installed `lai config` succeeds without a model server.
- The configuration semantic contract now uses `src/lai_config.py` as its first canonical path.
- Strict mypy scope increased from three to four files and passes.
- Full pytest: 250 passed + 85 subtests; full unittest: 250 passed.
- Ruff, compile/static checks, publication scan, VSIX packaging/inspection, and `make validate` passed.
- Harness Score 1.6.4 remains L4 Self-correcting at 100/108 (93%); no score-only feature was added.
- Public runtime and extension versions remain `0.4.0-beta.24`; no release notes, tag, PR, push, or GitHub release mutation occurred for this internal spec.
