# Spec: spec workflow modularization

## Metadata
- Mode: `full`
- Status: `complete`
- Target: `0.4.0 stabilization milestone`

## Goal
Continue typed monolith reduction by extracting deterministic spec parsing, active-spec selection, traceability validation, and prompt-context rendering into a dedicated standard-library-only module while preserving fail-closed behavior and runtime compatibility.

## Context and Constraints
- Spec workflow is deterministic and currently occupies a self-contained block in `src/local-agent`.
- Exactly one active spec may exist; malformed, symlinked, or multiply-active spec states must continue to fail closed.
- Existing runtime callers and tests rely on `agent.parse_spec`, `agent.load_active_spec`, and `agent.render_active_spec_context`.
- The public version remains `0.4.0-beta.24` throughout this internal milestone work.

## Requirements
### REQ-001
**Typed spec module**
Create `src/lai_specs.py` with typed spec metadata, parser, active-spec loader, required-section/traceability enforcement, and context renderer.

### REQ-002
**Fail-closed compatibility**
Preserve filename filtering, symlink rejection, multiple-active rejection, workflow/status validation, requirement-ID validation, validation coverage, and full-spec traceability coverage.

### REQ-003
**Runtime compatibility**
Keep `src/local-agent` compatibility helpers so callers continue using the same names while root-sensitive operations use the current runtime `ROOT`.

### REQ-004
**Installed-runtime compatibility**
Install `lai_specs.py` beside `local-agent` and prove installed deterministic `lai spec` behavior works without model execution or Python package installation.

### REQ-005
**Semantic navigation**
Make `src/lai_specs.py` the first canonical path for the `spec-workflow` semantic subsystem.

### REQ-006
**Strict type-check ratchet**
Add `src/lai_specs.py` to the existing strict mypy scope without removing any previously typed file.

### REQ-007
**Regression and milestone discipline**
Add focused regression coverage, pass the local gates, and keep all public release/version metadata unchanged until the stabilization milestone is ready as a whole.

## Acceptance Criteria
- spec implementation logic no longer lives in the monolithic runtime except compatibility wrappers;
- existing valid/invalid spec tests and active-spec prompt injection stay behaviorally compatible;
- installed `lai spec` works with the extracted module present;
- strict mypy passes with five files in the ratchet;
- semantic navigation points to the extracted spec module;
- no new dependency, model/network/Git authority, version bump, tag, push, PR, or release occurs for this spec alone.

## Validation
- `REQ-001`: inspect/type-check `src/lai_specs.py`.
- `REQ-002`: run all parse/load/render spec regressions, including symlink and multiple-active cases.
- `REQ-003`: assert compatibility helpers resolve through the extracted module and root-sensitive behavior still honors patched `agent.ROOT`.
- `REQ-004`: run isolated install smoke and installed `lai spec`.
- `REQ-005`: assert semantic JSON puts `src/lai_specs.py` first for `spec-workflow`.
- `REQ-006`: run quality-sensor ratchet plus `make typecheck`.
- `REQ-007`: run focused/full local gates and assert release/version files remain unchanged.
- Full local milestone gate: `make lint`, `make typecheck`, `make check`, `make test-dev`, `make test`, `make harness-score-gate`, `make validate`.

## Non-Goals
- Do not change the spec Markdown schema or add new workflow/status values.
- Do not weaken active-spec safety or make specs override repository rules.
- Do not extract policy, tools, control plane, release, update intelligence, or context ranking in this spec.
- Do not add third-party runtime dependencies or package-manager installation.
- Do not publish this internal spec as its own beta release.

## Implementation Notes
- Keep `parse_spec` directly re-exportable because it has no repository-global dependency.
- Wrap root-sensitive `load_active_spec` and `render_active_spec_context` in `src/local-agent` so patched/test runtime roots remain authoritative.
- Use a typed dictionary for parsed specs and Literal workflow/status types.
- Preserve the 6000-character bounded spec context and existing user-visible messages.

## Traceability
- `REQ-001` -> `src/lai_specs.py`.
- `REQ-002` -> spec parsing/loading regressions.
- `REQ-003` -> `src/local-agent` compatibility wrappers and prompt-injection tests.
- `REQ-004` -> `scripts/install-local.sh` and install smoke.
- `REQ-005` -> `src/lai_semantics.py` and semantic tests.
- `REQ-006` -> `mypy.ini` and quality-sensor tests.
- `REQ-007` -> full local gates plus unchanged public release metadata.


## Validation Evidence

- Extracted deterministic spec parsing, active-spec selection, traceability checks, and context rendering into typed `src/lai_specs.py`; `src/local-agent` decreased from 13,090 to 12,978 lines.
- Root-sensitive compatibility wrappers preserve the runtime `ROOT` as authoritative while direct parser helpers are re-exported.
- Differential comparison against local pre-extraction commit `12cf1d8` matched valid full/quick specs, invalid mode/requirement/validation/traceability errors, draft handling, and multiple-active fail-closed behavior exactly.
- Isolated install smoke confirms `lai_specs.py` is installed beside `local-agent` and installed `lai spec` reports deterministic status without model execution.
- The `spec-workflow` semantic contract now uses `src/lai_specs.py` as its first canonical path.
- Strict mypy scope increased from four to five files and passes.
- Full pytest: 251 passed + 85 subtests; full unittest: 251 passed.
- Ruff, compile/static checks, publication scan, VSIX packaging/inspection, Harness Score L4 100/108 (93%), and `make validate` all passed.
- Public runtime and extension versions remain `0.4.0-beta.24`; no release metadata, push, PR, tag, or GitHub release mutation occurred for this internal spec.
