# GitHub publishing metadata

## Repository

- **Name:** `lai-harness`
- **Display name:** lai harness
- **Description/About:** Local, auditable coding agent for VS Code, optimized for small LLMs via llama.cpp with compact tools, batch patching, validation guards, metrics, handoff, and forensic audit.
- **Website:** leave empty until project documentation has a stable public URL.

## Topics

`local-ai`, `coding-agent`, `ai-agent`, `vscode`, `vscode-extension`, `llama-cpp`, `llm`, `developer-tools`, `devtools`, `python`, `javascript`, `wsl`, `local-llm`, `tool-calling`, `observability`, `ai-security`, `code-review`, `automation`

## README short pitch

Small local models become much more useful when the agent architecture is optimized around them. lai harness combines compact mode-specific tools, batch inspection and patching, validation and evidence gates, local metrics, forensic audit, run history, sanitized run export, readiness checks, and Git-aware handoff in a VS Code workflow.

## Release v0.4.0-beta.3

Use the release notes in [Release notes](RELEASE-NOTES.md) as the GitHub Release body for `v0.4.0-beta.3`.

**Title:** lai harness v0.4.0-beta.3 — release polish

Attach the inspected VSIX from `scripts/package-vsix.sh` only after `make validate`, `lai readiness`, `lai release-check --target 0.4.0-beta.3 --json`, and GitHub CI pass on both `main` and the tag.

## LinkedIn project description

Built lai harness, an experimental local coding agent for VS Code, to study how constrained agent architecture improves the usefulness of small local LLMs. I designed mode-specific tool schemas, batch inspection and patching, validation and evidence gates, post-patch sanity checks, metrics, forensic audit, run history, sanitized diagnostics, readiness checks, and Git-aware handoff to higher-context agents. The project evolved through profiling and real failure analysis across Python, JavaScript, llama.cpp, WSL/Windows, and VS Code extension development. Results are presented as hardware-specific experiments, not universal performance claims.

## Portfolio description

lai harness is a compact local coding-agent harness for small LLMs, featuring bounded tools, batch operations, validation/evidence guards, observability, audit trails, run export, readiness gates, and cross-agent context handoff.

## GitHub profile / pinned repository

lai harness explores a practical question: how much more useful can a small local model become when prompts, schemas, tool rounds, validation, release gates, and auditability are designed around its constraints?
