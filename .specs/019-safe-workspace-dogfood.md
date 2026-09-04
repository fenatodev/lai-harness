# Spec: Safe workspace dogfood

## Metadata

- Mode: `full`
- Status: `done`

## Goal

Provide a deterministic way to create, inspect, and clean disposable workspaces so write-capable LAI modes can be dogfooded away from `main` and release branches.

## Requirements

### REQ-001

Add a read-only status command for safe workspaces.

### REQ-002

Add a deterministic create command that copies tracked repository files into a standalone disposable Git repository on branch `test/lai-smoke`.

### REQ-003

Add a clean command that can remove only paths inside the configured safe workspace base.

### REQ-004

Document the workflow and expose it through the `lai workspace` wrapper command.

## Acceptance Criteria

- `lai workspace status` and `lai workspace status --json` work without model calls.
- `lai workspace create --name smoke` creates a disposable Git repository outside the source checkout.
- `lai workspace clean smoke` removes only the disposable workspace.
- tests cover creation, status, cleanup, path refusal and installed CLI routing.

## Validation

- `REQ-001`: `python3 -m unittest tests.test_local_agent.LocalAgentTest.test_safe_workspace_create_status_and_clean -v`
- `REQ-002`: `python3 -m unittest tests.test_local_agent.LocalAgentTest.test_safe_workspace_create_status_and_clean -v`
- `REQ-003`: `python3 -m unittest tests.test_local_agent.LocalAgentTest.test_safe_workspace_clean_refuses_outside_path -v`
- `REQ-004`: `PYTHONPATH=tests python3 -m unittest tests.test_install_smoke.IsolatedInstallSmokeTest.test_install_doctor_sample_repo_and_deterministic_commands -v`

## Context and Constraints

The command must not mutate the source checkout except for normal documentation/code changes in this implementation branch. Runtime workspace creation must operate outside `ROOT` by default.

## Non-Goals

- No GitHub mutation.
- No branch protection API setup.
- No model call.
- No automatic execution of `lai implement` inside the disposable workspace.

## Implementation Notes

Use tracked files as the seed set so untracked files, secrets, virtual environments and generated artifacts are not copied into the dogfood workspace.

## Traceability

- `REQ-001` -> `handle_safe_workspace`, `render_safe_workspace_status`
- `REQ-002` -> `create_safe_workspace`, `copy_tracked_repository_files`
- `REQ-003` -> `clean_safe_workspace`, `ensure_safe_workspace_child`
- `REQ-004` -> `src/lai`, `docs/SAFE-WORKSPACES.md`, install smoke
