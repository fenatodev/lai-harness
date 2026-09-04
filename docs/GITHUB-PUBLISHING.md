# GitHub publishing metadata

Public metadata for the repository and beta releases.

## Repository

**Name:** `lai-harness`

**Clone URL:** `https://github.com/fenatodev/lai-harness.git`

**Description:** Local, auditable coding agent for VS Code, optimized for small LLMs via llama.cpp with compact tools, batch patching, validation guards, metrics, handoff and forensic audit.

## Release v0.4.0-beta.7

Use `lai release-pack --target 0.4.0-beta.7 --with-vsix --json` to generate local release files before publishing manually.

Use `lai project-handoff --target 0.4.0-beta.7 --out /tmp/lai-harness-project-handoff-v0.4.0-beta.7 --force --json` before moving work to another chat.

**Title:** lai harness v0.4.0-beta.7 — project handoff

The GitHub Release body should come from the generated `release-body.md` file or from [Release notes](RELEASE-NOTES.md).

Attach the inspected VSIX from the release pack only after `make validate`, `lai readiness`, `lai workspace status --json`, `lai project-handoff --target 0.4.0-beta.7 --json`, `lai release-check --target 0.4.0-beta.7 --json`, and GitHub CI pass on both `main` and the tag.

Mark the release as a pre-release while the project remains in beta.

## Non-goals

Do not upload model weights, API keys, logs, audit state, metrics, local handoffs, recovery checkpoints, or generated safe workspaces.
