# Architecture

LAI has four runtime layers: the VS Code chat participant, the Python harness, an authenticated OpenAI-compatible server, and a user-supplied model.

## Request flow

1. `@lai` receives a command and prompt.
2. The extension adds bounded context: active filename, at most eight diagnostics for write/debug modes, and up to 800 characters of selected text.
3. It starts `local-agent` in the selected workspace.
4. The harness resolves the Git root, loads workspace state, the active repository spec, and the mode skill, selects only that mode's tool schemas, and calls the local endpoint.
5. Tool results return to the model until it answers or reaches the mode's round limit.
6. State, metrics, and applicable audit events are persisted outside the repository.

## Components

### VS Code extension

`vscode-extension/extension.js` implements the chat participant and streams stdout as Markdown. Recognized tool activity from stderr becomes progress UI. `lai.agentPath` overrides the default `~/.local/bin/local-agent` executable.

### Python harness

`src/local-agent` uses only Python's standard library. It owns prompting, tool dispatch, mode gates, output limits, endpoint authentication, persistence, and audit correlation.

### Skills and tool schemas

Skills are compact mode contracts stored in `skills/`. Tools are selected by mode, so a review model does not receive write-tool schemas and a plan model receives only `inspect` and `search`. `inspect` batches up to eight files. `patch` validates up to six exact replacements in memory before writing any target.

### Repository specs

Numbered specs under `.specs/` define the requested change. At most one may be `active`; multiple active specs, invalid requirement IDs, missing validation references, and symlinked spec paths fail closed. Draft and complete specs do not affect runtime. The active spec is injected as normative context beneath repository safety rules.

### llama.cpp and model

The reference setup uses `llama-server` with an OpenAI-compatible chat-completions endpoint. The default model string records the experimental baseline but can be replaced with `LAI_MODEL`. LAI does not download or redistribute models.

### Workspace state

State is keyed by a SHA-256-derived workspace identity under `$LAI_DATA_DIR/state`. A compact Markdown and JSON handoff is also updated at the data-root level. Stored content can include task text, repository path, recent filenames, validation output, branch, and Git status.

### Metrics and audit

Metrics use one `run_id` per process invocation and record API/tool duration, token usage, and schema count. Audit events record patch paths, before/after hashes, post-patch sanity, validation, and final status. These stores are operational records, not telemetry uploads.

## Guard sequence for implementation

```text
inspect context → batch patch → deterministic syntax/added-line checks
    → compact model sanity → project validation → acceptance check → final answer
```

A clean sanity result never replaces project tests. See the security and observability documents for trust boundaries and retained data.
