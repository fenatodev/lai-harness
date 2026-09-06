# GitHub publishing metadata

Public repository metadata and release presentation for `fenatodev/lai-harness`.

## Repository

**Name:** `lai-harness`

**Clone URL:** `https://github.com/fenatodev/lai-harness.git`

**Description:** Local-first, auditable coding harness for small LLMs: compact tools, deterministic policy, validation, observability, control plane, and protected releases.

**Topics:** `ai-agent`, `agentic-coding`, `ai-security`, `automation`, `code-review`, `coding-agent`, `developer-tools`, `devtools`, `llama-cpp`, `llm`, `local-ai`, `local-first`, `local-llm`, `observability`, `python`, `release-automation`, `tool-calling`, `vscode`, `vscode-extension`, `wsl`

The README is the primary landing page. Keep Wiki/Projects disabled unless they gain an explicit maintained purpose; project documentation and roadmap/history remain version-controlled.

## Visual presentation

Approved diagrams live under `docs/assets/`. Review `docs/assets/visual-assets.json` on every version bump. Regenerate a diagram only when its architecture changed; otherwise advance the review marker after explicit verification.

## Release target

Generate publication files with `lai release-pack --target <target-version> --with-vsix --json`. The resulting summary is authoritative for:

- exact target version and tag;
- release channel (`prerelease` or `stable`);
- expected GitHub `prerelease` flag;
- inspected VSIX path.

The generated `release-body.md` should come from the exact target section in [Release notes](RELEASE-NOTES.md). Before merge, protected `main` must require Python 3.11, Python 3.12, Publication gates, and Harness Score L4. After publication, run `lai release-governance --target <target-version> --remote --json` to verify branch protection, release metadata/channel, and the VSIX digest.

## Publication hygiene

Do not upload model weights, API keys, control tokens, local benchmark result JSONL, logs, audit state, metrics, handoffs, recovery checkpoints, safe workspaces, or machine-specific operational state.

Public update/model claims must distinguish reproducible evidence from untrusted upstream prose or preliminary local observations. A candidate release/model is evidence for review, never automatic authority to apply or replace anything. Keep public claims consistent with [Security model](SECURITY-MODEL.md).
