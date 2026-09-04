# GitHub publishing metadata

## Repository

- **Name:** `lai-local-agent`
- **Display name:** lai harness
- **Description/About:** Local, auditable coding agent for VS Code, optimized for small LLMs via llama.cpp with compact tools, batch patching, validation guards, metrics, handoff and forensic audit.
- **Website:** leave empty until project documentation has a stable public URL.

## Topics

`local-ai`, `coding-agent`, `ai-agent`, `vscode`, `vscode-extension`, `llama-cpp`, `llm`, `developer-tools`, `devtools`, `python`, `javascript`, `wsl`, `local-llm`, `tool-calling`, `observability`, `ai-security`, `code-review`, `automation`

## README short pitch

Small local models become much more useful when the agent architecture is optimized around them. LAI combines compact mode-specific tools, batch inspection and patching, validation and evidence gates, local metrics, forensic audit, and Git-aware handoff in a VS Code workflow.

## Release v0.3.0

**Title:** LAI v0.3.0 — First public source release

**Body:**

lai harness is a compact, auditable VS Code coding harness designed for local LLMs and low-overhead tool use. This first public release extracts the working 0.2.3 experiment into a sanitized, configurable distribution.

Highlights:

- 14 chat commands and 8 focused mode skills;
- batch inspection and transactional exact-replacement patching;
- validation, acceptance, evidence, debug-evidence, and post-patch sanity guards;
- local metrics, workspace handoff, and forensic audit JSONL;
- configurable endpoint, model, data paths, key path, and VS Code agent path;
- synthetic smoke tests and complete security/architecture documentation.

lai harness is experimental and is not a sandbox. Models, GGUF weights, llama.cpp, VS Code, and third-party templates are not included or licensed by lai harness's MIT license.

## LinkedIn project description

Built LAI, an experimental local coding agent for VS Code, to study how constrained agent architecture improves the usefulness of small local LLMs. I designed mode-specific tool schemas, batch inspection and patching, validation and evidence gates, post-patch sanity checks, metrics, forensic audit, and Git-aware handoff to higher-context agents. The project evolved through profiling and real failure analysis across Python, JavaScript, llama.cpp, WSL/Windows, and VS Code extension development. Results are presented as hardware-specific experiments, not universal performance claims.

## Portfolio description

lai harness is a compact local coding-agent harness for small LLMs, featuring bounded tools, batch operations, validation/evidence guards, observability, audit trails, and cross-agent context handoff.

## GitHub profile / pinned repository

lai harness explores a practical question: how much more useful can a small local model become when prompts, schemas, tool rounds, validation, and auditability are designed around its constraints?
