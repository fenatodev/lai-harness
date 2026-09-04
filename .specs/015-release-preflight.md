# Spec: Release Preflight and Public Mode Aliases

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Make release operation safer and more deterministic before beta by preloading release readiness evidence, exposing public CLI aliases for mode skills, and adding a model-free release check.

## Requirements

### REQ-001

Release mode must receive a read-only preflight context with current version, repository state, tag state, readiness status, and preferred validation commands.

### REQ-002

The `lai` wrapper must dispatch public mode aliases such as `lai diagnose`, `lai ci-fix`, and `lai release` to their matching local-agent modes.

### REQ-003

The release skill must direct small local models to use Makefile/script validation commands instead of probing ad-hoc pytest/python commands.

### REQ-004

A deterministic `lai release-check` command must report release posture without calling the model or mutating Git state.

### REQ-005

The change must preserve existing release safety: no automatic tag, merge, push, publication, upload, or destructive operation.

## Acceptance Criteria

- `lai release "respond only: ok"` returns `ok` without calling the model.
- `lai release-check --json` returns release posture with `release_safety`.
- Release preflight includes `make check`, `make test-dev`, `make test`, and `make validate` when those targets are present.
- `make validate` passes.
- Public docs mention release preflight and CLI aliases.

## Validation

- `REQ-001`: `tests.test_local_agent.LocalAgentTest.test_release_preflight_context_prefers_project_commands`
- `REQ-002`: `tests.test_install_smoke.IsolatedInstallSmokeTest.test_install_doctor_sample_repo_and_deterministic_commands`
- `REQ-003`: release skill file assertions and the release preflight test
- `REQ-004`: `tests.test_local_agent.LocalAgentTest.test_release_check_is_deterministic_and_read_only`
- `REQ-005`: existing policy tests keep release mode read-only

## Context and Constraints

Release decisions remain human-controlled. The agent may inspect state and suggest commands, but it must not mutate Git release state.

## Non-Goals

- Creating a GitHub Release automatically.
- Signing tags.
- Uploading packages.
- Replacing `make validate` with a new build system.

## Implementation Notes

The preflight is generated inside `src/local-agent` before model reasoning. It uses deterministic local repository inspection and existing readiness checks.

## Traceability

- `REQ-001` -> `render_release_preflight_context`
- `REQ-002` -> `src/lai` mode-alias dispatch
- `REQ-003` -> `.agents/skills/release/SKILL.md` and `skills/release.txt`
- `REQ-004` -> `render_release_check` and `collect_release_check`
- `REQ-005` -> `evaluate_tool_policy` release read-only coverage
