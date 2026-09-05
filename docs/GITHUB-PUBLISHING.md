# GitHub publishing metadata

Public repository metadata and release presentation for `fenatodev/lai-harness`.

## Repository

**Name:** `lai-harness`

**Clone URL:** `https://github.com/fenatodev/lai-harness.git`

**Description:** Local-first, auditable coding harness for small LLMs: compact tools, deterministic policy, validation, observability, control plane, and protected releases.

**Topics:**

`ai-agent`, `agentic-coding`, `ai-security`, `automation`, `code-review`, `coding-agent`, `developer-tools`, `devtools`, `llama-cpp`, `llm`, `local-ai`, `local-first`, `local-llm`, `observability`, `python`, `release-automation`, `tool-calling`, `vscode`, `vscode-extension`, `wsl`

The repository README is the primary landing page. Keep Wiki/Projects disabled unless they gain an explicit maintained purpose; project documentation lives under `docs/` and roadmap/history live in version control.

## Visual presentation

The approved diagrams are versioned under `docs/assets/`. `docs/assets/visual-assets.json` must be reviewed on every version bump. Regenerate a diagram only when the architecture it describes changes; otherwise update the review marker after confirming the diagrams remain accurate.

## Release v0.4.0-beta.19

Use `lai release-pack --target 0.4.0-beta.19 --with-vsix --json` to generate local publication files.

**Expected title:** lai harness v0.4.0-beta.19 — release metadata correctness

The generated `release-body.md` must come from the exact `## lai harness v0.4.0-beta.19` section in [Release notes](RELEASE-NOTES.md). Do not substitute text from older `### Release body for GitHub` markers.

Before merge, protected `main` must require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`.

After publication, run `lai release-governance --target 0.4.0-beta.19 --remote --json` to verify branch protection, pre-release metadata, and the VSIX digest when attached.

## Publication hygiene

Do not upload model weights, API keys, control tokens, local logs, audit state, metrics, handoffs, recovery checkpoints, safe workspaces, or machine-specific operational state.

Keep public claims consistent with [Security model](SECURITY-MODEL.md): local interactive `bash` is not sandboxed; remote read-only profiles are shell-free; remote work writes only to disposable safe workspaces; approved promotion is hash-bound, revalidated, and targets a dedicated feature worktree rather than the active checkout; `lai-gateway` remains a separate companion project.