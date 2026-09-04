# GitHub publishing metadata

Public metadata for the repository and beta releases.

## Repository

**Name:** `lai-harness`

**Clone URL:** `https://github.com/fenatodev/lai-harness.git`

**Description:** Local, auditable coding agent for VS Code, optimized for small LLMs via llama.cpp with compact tools, batch patching, validation guards, metrics, handoff and forensic audit.

## Release v0.4.0-beta.9

Use `lai release-pack --target 0.4.0-beta.9 --with-vsix --json` to generate local release files.

**Title:** lai harness v0.4.0-beta.9 — self-correcting development harness

The GitHub Release body should come from generated `release-body.md` or [Release notes](RELEASE-NOTES.md). Mark the release as a pre-release while the project remains beta.

Before merge, ensure protected `main` requires `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`.

After publication, run `lai release-governance --target 0.4.0-beta.9 --remote --json` to verify branch protection, pre-release metadata, and the VSIX digest when attached.

## Non-goals

Do not upload model weights, API keys, logs, audit state, metrics, local handoffs, recovery checkpoints, or generated safe workspaces.
