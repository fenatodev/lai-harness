# Spec: Node 24 CI supply-chain hardening

## Metadata
- Mode: `full`
- Status: `complete`

## Goal
Remove the live GitHub Actions Node 20 deprecation warning and make CI action dependencies immutable, auditable, and reviewable without changing LAI runtime authority or model behavior.

## Requirements
### REQ-001
Migrate GitHub-maintained workflow actions to reviewed Node 24-compatible releases pinned to immutable full commit SHAs.

### REQ-002
Run publication packaging on explicit Node.js 24 and disable setup-node package-manager caching when no npm dependency cache is required.

### REQ-003
Add reviewable automated dependency tracking for GitHub Actions without reintroducing floating workflow references.

### REQ-004
Add regression coverage that fails if official GitHub Actions return to mutable major tags, legacy Node 20 action majors, unreviewed official action dependencies, or Node.js 20 publication packaging.

### REQ-005
Document the SHA-pin policy so future agents preserve reviewed immutable references and use normal protected-main review for upgrades.

### REQ-006
Keep runtime capabilities, remote authority, model behavior, Python runtime dependencies, promotion behavior, and release authority unchanged.

## Acceptance Criteria
- `actions/checkout` is pinned to reviewed v7.0.1 commit `3d3c42e5aac5ba805825da76410c181273ba90b1`.
- `actions/setup-python` is pinned to reviewed v7.0.0 commit `5fda3b95a4ea91299a34e894583c3862153e4b97`.
- `actions/setup-node` is pinned to reviewed v7.0.0 commit `820762786026740c76f36085b0efc47a31fe5020`.
- All three exact upstream releases declare `runs.using: node24`.
- Publication selects Node.js 24 and disables unnecessary setup-node package-manager caching.
- Dependabot tracks the `github-actions` ecosystem weekly.
- Focused workflow regressions, Python 3.11/3.12 tests, static checks, publication scan, and VSIX packaging remain green.

## Validation
- `REQ-001`: exact upstream tag/SHA/runtime verification plus `tests/test_github_actions_hardening.py`.
- `REQ-002`: workflow regression plus publication gate.
- `REQ-003`: Dependabot configuration regression.
- `REQ-004`: focused unittest sensor and full CI/publication runs.
- `REQ-005`: `AGENTS.md` and development-harness documentation review.
- `REQ-006`: full regression suite, typecheck, publication scan, and release preflight.

## Context and Constraints
GitHub's beta.16 tag run reported that `actions/checkout@v4` and `actions/setup-python@v5` were Node 20 actions being forced onto Node 24. Current reviewed upstream releases are checkout v7.0.1, setup-python v7.0.0, and setup-node v7.0.0. GitHub-hosted runners satisfy their runtime requirements.

The project already pins the third-party Harness Score action to a full SHA. This cut extends the same immutable-reference discipline to GitHub-maintained actions and uses Dependabot only to propose reviewable pin updates.

Development dependencies may be executed in disposable validation environments, but the active user environment must not be mutated automatically.

## Non-Goals
- No work solely to increase Harness Score.
- No MCP, subagent, session, browser/web, or provider feature.
- No new runtime dependency.
- No new remote shell, Git mutation, PR, merge, tag, or release authority.
- No self-hosted-runner support claim beyond documented upstream requirements.

## Traceability
- `REQ-001` -> `.github/workflows/ci.yml`, `.github/workflows/harness-score.yml`, workflow regression sensor.
- `REQ-002` -> `.github/workflows/ci.yml`, workflow regression sensor.
- `REQ-003` -> `.github/dependabot.yml`, workflow regression sensor.
- `REQ-004` -> `tests/test_github_actions_hardening.py`, existing CI/publication gates.
- `REQ-005` -> `AGENTS.md`, `docs/DEVELOPMENT-HARNESS.md`.
- `REQ-006` -> existing control-plane, guard, promotion, install-smoke, release, typecheck, and publication regression suites.
