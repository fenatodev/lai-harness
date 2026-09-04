# GitHub publishing

Public metadata for the repository and beta releases.

## Repository

**Owner:** `fenatodev`

**Name:** `lai-harness`

**Description:** Local, auditable coding agent for VS Code, optimized for small LLMs via llama.cpp with compact tools, batch patching, validation guards, metrics, handoff and forensic audit.

## Release v0.4.0-beta.4

Use the release notes in [Release notes](RELEASE-NOTES.md) as the GitHub Release body for `v0.4.0-beta.4`.

**Title:** lai harness v0.4.0-beta.4 — safe workspace dogfood

Attach the inspected VSIX from `scripts/package-vsix.sh` only after `make validate`, `lai readiness`, `lai workspace status --json`, `lai release-check --target 0.4.0-beta.4 --json`, and GitHub CI pass on both `main` and the tag.

Mark the release as a pre-release while the project remains in beta.
