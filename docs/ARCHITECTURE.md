# Architecture

lai harness has four runtime layers: the VS Code chat participant, the Python harness, an authenticated OpenAI-compatible server, and a user-supplied model.

![lai harness core architecture](assets/core-architecture.png)

The diagram is a documentation overview; runtime code, policy, and the security model are authoritative.

## Request flow

1. `@lai` receives a command and prompt.
2. The extension adds bounded context: active filename, at most eight diagnostics for write/debug modes, and up to 800 characters of selected text.
3. It starts `local-agent` in the selected workspace.
4. The harness resolves the Git root, loads workspace state, the active repository spec, and the mode skill, and builds bounded ranked context metadata for selected modes before inference.
5. Every tool action crosses the central policy boundary before dispatch; `ASK` stops the run for user action and `DENY` blocks execution.
6. Allowed tool results return to the model until it answers or reaches the mode's round limit.
7. Runtime checkpoint, workspace state, metrics, and applicable audit events are persisted outside the repository.
8. Normal completion marks the checkpoint terminal; an abrupt interruption leaves a non-terminal checkpoint that can be inspected later.

## Components

### VS Code extension

`vscode-extension/extension.js` implements the chat participant and streams stdout as Markdown. Recognized tool activity from stderr becomes progress UI. `lai.agentPath` overrides the default `~/.local/bin/local-agent` executable.

### Python harness

`src/local-agent` uses only Python's standard library. It owns prompting, centralized policy evaluation, tool dispatch, mode gates, output limits, endpoint authentication, persistence, and audit correlation.

### Local control plane

`lai serve` is an optional loopback-only HTTP/JSON adapter implemented inside the Python harness with the standard library. It uses a bearer token separate from the llama.cpp key. Beta.15 keeps serialized read-only runs (`plan`, `review`, `security`, `diagnose`, `release`) and isolated work runs (`implement`, `fix`, `refactor`, `ci-fix`). Capability reduction still happens before inference: no control child receives generic `bash` or Git mutation tools. Work children run from a unique safe workspace copied from tracked source contents, receive repository-confined file tools plus structured `validate`, and return bounded Git/diff evidence. Remote validation runs through a fixed Docker sandbox with no network, no host home, no Docker socket, dropped capabilities, and a read-only container root. Successful work results may expose a deterministic promotion proposal whose approval is bound to the complete patch SHA-256. Promotion repeats sandbox validation, rechecks source and patch drift, then applies the exact patch to a dedicated `lai/promotion-*` Git worktree/feature branch. The active source checkout remains untouched. `lai-gateway` may proxy this surface to private mobile clients without making the harness bind to LAN, tailnet, or public interfaces.

### Skills and tool schemas

Skills are compact mode contracts stored in `skills/`. Tools are selected by mode, so a review model does not receive write-tool schemas and a plan model receives only `inspect` and `search`. `inspect` batches up to eight files. `patch` validates up to six exact replacements in memory before writing any target.

### Repository specs

Numbered specs under `.specs/` define the requested change. At most one may be `active`; multiple active specs, invalid requirement IDs, missing validation references, and symlinked spec paths fail closed. Draft and complete specs do not affect runtime. The active spec is injected as normative context beneath repository safety rules.

### Configuration boundary

Before model runtime, the harness normalizes configuration from leading CLI flags, `LAI_*` environment variables, `[lai]` TOML values, and defaults. Unknown TOML keys and invalid types fail closed. `lai config` reports effective values and path diagnostics without starting or probing the model server and never prints API key contents.

### Context intelligence

For `plan`, `debug`, `fix`, `implement`, and `refactor`, the harness ranks a bounded repository inventory before inference. Signals include task/path terms, live Git changes, verified recent/modified workspace paths, active-spec path references, known manifests, and bounded text sampling. Only candidate path, score, and reason metadata are injected; file contents still require normal inspection. `lai context <task>` exposes the same ranking without calling the model.

### Policy and lifecycle

Every builtin tool action is evaluated as `ALLOW`, `ASK`, or `DENY` before dispatcher execution. `ASK` never auto-executes and terminates the current run with `user_action_required`; `DENY` fails closed while allowing the model to choose a different safe action. Mode allowlists and validation guards remain independent defense-in-depth layers.

### llama.cpp and model

The reference setup uses `llama-server` with an OpenAI-compatible chat-completions endpoint. The default model string records the experimental baseline but can be replaced with `LAI_MODEL`. lai harness does not download or redistribute models.

### Runtime recovery

A versioned checkpoint under `$LAI_DATA_DIR/checkpoints` records run ID, mode, bounded task text, lifecycle phase, branch, Git status, tracked-file hashes, and the last tool name. Writes use same-directory atomic replacement. `lai recovery` inspects compatibility without the model; `lai resume` starts a fresh run only when live branch/status/hashes still match. Tool arguments are not stored for replay.

### Workspace state

State is keyed by a SHA-256-derived workspace identity under `$LAI_DATA_DIR/state`. A compact Markdown and JSON handoff is also updated at the data-root level. Stored content can include task text, repository path, recent filenames, validation output, branch, and Git status.

### Metrics and audit

Metrics use one `run_id` per process invocation and record API/tool duration, token usage, and schema count. Audit events record policy decisions, checkpoint/recovery transitions, lifecycle outcomes, patch paths, before/after hashes, post-patch sanity, validation, and final status. These stores are operational records, not telemetry uploads.

## Guard sequence for implementation

```text
inspect context → batch patch → deterministic syntax/added-line checks
    → compact model sanity → project validation → acceptance check → final answer
```

A clean sanity result never replaces project tests. See the security and observability documents for trust boundaries and retained data.
