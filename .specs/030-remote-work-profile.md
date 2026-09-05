# Spec: remote work capability profile

## Metadata
- Mode: `full`
- Status: `complete`

## Goal
Allow authenticated control-plane clients such as lai-gateway, PWA, and Telegram to request bounded repository implementation work without exposing arbitrary shell execution, Git mutation, dependency installation, or system administration.

## Requirements
### REQ-001
Add a structured `validate` tool whose input is a small validation profile, never a shell command. Local use may execute recognized project validation argv directly; remote work validation must execute only inside the configured sandbox boundary.

### REQ-002
Validation profiles must support at least `test`, `check`, `lint`, `build`, `typecheck`, and `full`, selecting from existing Makefile targets, package scripts, or conservative language-native project commands. Missing recognized validation must fail cleanly without falling back to arbitrary shell.

### REQ-003
Integrate `validate` with existing write lifecycle guards, workspace state, metrics, audit, checkpoint transitions, assertion-failure protection, and post-write requirement enforcement. A successful structured validation must satisfy the same post-write gate as a successful recognized local bash validation.

### REQ-004
Add remote capability profiles for `implement`, `fix`, `refactor`, and `ci-fix`. Every work run must execute in a unique safe workspace copied from tracked current repository contents, never directly in the source checkout. The model may receive repository-confined read/write tools plus `validate`, but never `bash` or Git mutation tools.

### REQ-005
Remote validation must run through a fixed Docker sandbox invocation with no network, read-only container root, dropped capabilities, no-new-privileges, bounded processes/memory/CPU, no host home or Docker socket, and only the safe workspace writable. It may reuse explicitly recognized local runtime/dependency directories read-only. The harness must never pull a sandbox image automatically.

### REQ-006
Remote writes must retain repository confinement, symlink/stale-write checks, active-spec rules, patch sanity, validation requirements, and mode guards. Run records must expose the isolated workspace status, changed paths, and a bounded diff without mutating the source checkout.

### REQ-007
Control-plane status and run records must distinguish read-only and work-capable profiles clearly and report sandbox readiness. Existing read-only modes remain behaviorally compatible.

### REQ-008
Add deterministic tests proving structured validation argv/no-shell behavior, sandbox argv and secret isolation, missing-sandbox failure, lifecycle integration, remote work schemas without bash, source-checkout immutability, and real subprocess completion against a fake model in an isolated safe workspace.

## Acceptance Criteria
- A remote `implement` run can modify a file only in its disposable safe workspace, execute structured validation in the sandbox, and complete successfully.
- The source checkout remains byte-for-byte unchanged by the work run.
- No remote mode receives `bash`.
- No caller can inject an executable, cwd, env, shell syntax, or arbitrary validation command through the structured tool.
- Existing read-only control runs remain green.

## Validation
- `REQ-001` / `REQ-002`: unit tests for discovery and argv execution.
- `REQ-003`: lifecycle/recording integration tests.
- `REQ-004` / `REQ-006`: capability-schema, safe-workspace, and source-immutability tests.
- `REQ-005`: sandbox argv/network/home/socket tests.
- `REQ-007`: status/public-record tests.
- `REQ-008`: fake-model real-subprocess control-plane smoke.

## Context and Constraints
The current beta.13 control plane exposes only shell-free read-only modes. Local write modes already have strong repository write guards but rely on generic `bash` for post-write validation. Remote autonomy should be obtained by adding a narrower validation capability, not by exposing that shell.

## Non-Goals
- No arbitrary remote shell and no direct remote write to the source checkout.
- No commit, push, merge, tag, release publication, package installation, service control, or OS administration.
- No web search or MCP/Desktop Commander in this cut.
- No persistent conversational sessions in this cut.
- No approval execution protocol yet.

## Implementation Notes
Prefer one shared validation discovery layer with separate local and remote execution backends. The remote backend uses a pre-existing local container image only and must never mount host home or Docker socket. Do not parse or sanitize caller-supplied shell because callers never supply shell text. Capability reduction happens before model tool schemas are built.

## Traceability
- `REQ-001` -> `validate` tool schema, `tool_validate`, local/remote validation backends.
- `REQ-002` -> `validation_command_candidates`, `select_validation_command`, profile tests.
- `REQ-003` -> post-write progress guard, workspace/audit validation recording, structured-validation integration test.
- `REQ-004` -> `CONTROL_RUN_WORK_MODES`, capability maps, `create_control_work_workspace`.
- `REQ-005` -> `remote_validation_docker_argv`, sandbox readiness gate, real Docker isolation smoke.
- `REQ-006` -> existing write guards plus `collect_control_workspace_result` and bounded public diff.
- `REQ-007` -> `control_status_payload`, per-run `tool_profile`, sandbox readiness/status tests.
- `REQ-008` -> `tests/test_control_plane.py` real-child fake-model smoke and source-checkout immutability assertions.
