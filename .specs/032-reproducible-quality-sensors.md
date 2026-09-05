# Spec: reproducible quality sensors

## Metadata
- Mode: `full`
- Status: `complete`

## Goal
Make Python development sensors reproducible and add an enforceable static type-checking ratchet without pretending the current monolithic extensionless runtime is fully typed.

## Requirements
### REQ-001
Add a canonical, fully resolved development sensor lock derived from a small human-maintained input manifest; runtime installation must remain standard-library-only.

### REQ-002
Add a pinned mypy sensor and an explicit configuration that initially checks the Python development guardrail hooks with strict typing.

### REQ-003
Add type annotations to the checked hook surface without weakening its fail-closed behavior, repository confinement, or subprocess boundaries.
### REQ-004
Expose a canonical `make typecheck` command and run it in CI before the existing regression/static checks.

### REQ-005
Keep the full publication gate deterministic and ensure the dependency-free `make test` path remains available.

### REQ-006
Update public development documentation and roadmap state so completed beta.15 work is no longer listed as pending and the type-check scope is not overstated.

### REQ-007
Add regression coverage that asserts the lock/config/CI wiring and prevents removal of the type-check ratchet by accident.

### REQ-008
The cut must retain Harness Score L4 and should raise the measured score only through real repository capabilities, not empty marker files.

## Acceptance Criteria
- Development sensor versions and transitive dependencies resolve from a committed canonical lock.
- `make typecheck` succeeds on its declared strict scope.
- CI installs the canonical lock and executes type checking on Python 3.11 and 3.12.
- Runtime installation still installs no third-party Python packages.
- Existing tests, static checks, publication scan, VSIX packaging, and Harness Score L4 remain green.
## Validation
- `REQ-001`: lock generation metadata, CI install path, and regression assertions.
- `REQ-002` / `REQ-003`: mypy strict run over `.cursor/hooks/*.py` plus existing hook behavior tests.
- `REQ-004`: Makefile target and CI workflow regression assertions.
- `REQ-005`: `make test`, `make check`, and `make validate`.
- `REQ-006`: documentation/publication scan and roadmap review.
- `REQ-007`: focused repository-configuration tests.
- `REQ-008`: `make harness-score` and `make harness-score-gate`.

## Context and Constraints
The runtime remains concentrated in the extensionless `src/local-agent` script. Pretending that adding a type-checker config makes that entire runtime typed would be misleading. This cut establishes a strict, passing boundary on small Python guardrail modules and a ratchet that can expand as runtime subsystems are split into importable modules.

Development tooling may be resolved or executed in disposable locations for validation, but the active user environment must not be mutated automatically.

## Non-Goals
- No MCP configuration merely to gain Harness Score points.
- No custom subagent definition before real delegation/orchestration exists.
- No broad runtime refactor solely to satisfy a type checker.
- No runtime third-party dependency.
- No release tag, merge, push, upload, or publication in this implementation step.

## Traceability
- `REQ-001` -> `requirements-dev.in`, generated `requirements.txt`, CI install step, config regression test.
- `REQ-002` -> `mypy.ini`, pinned mypy in sensor manifest, `make typecheck`.
- `REQ-003` -> typed `.cursor/hooks/feedback_check.py` and `.cursor/hooks/guard_shell.py`; existing hook tests.
- `REQ-004` -> `Makefile`, `.github/workflows/ci.yml`, workflow regression test.
- `REQ-005` -> existing dependency-free unittest path and complete publication gates.
- `REQ-006` -> `ROADMAP.md`, `AGENTS.md`/README development commands as needed.
- `REQ-007` -> repository configuration regression coverage.
- `REQ-008` -> Harness Score measurement/gate evidence.
