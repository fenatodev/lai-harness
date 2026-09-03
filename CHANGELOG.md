# Changelog

All notable changes to this project are documented here.

## [0.4.0-alpha.2] - Unreleased

### Added

- Portable Python search fallback when `ripgrep` is unavailable.
- Regression coverage for authenticated server readiness, VS Code workspace safety, bounded agent exploration, stderr diagnostics, and search fallback.

### Changed

- Bound pre-write exploration in `fix`, `refactor`, and `implement` modes and force a write phase or explicit `IMPLEMENTATION_IMPOSSIBLE` outcome.
- Surface exploration-budget and overall-round limits through metrics and audit diagnostics.
- Preserve non-progress agent stderr diagnostics in the VS Code extension instead of collapsing failures into generic exit-code messages.

### Security

- Model-server readiness now requires authenticated access to succeed while unauthenticated `/props` access is rejected.
- VS Code write modes require an unambiguous workspace, avoid silently switching to an external active file, and exclude external-file context from write requests.

## [0.4.0-alpha.1] - 2026-09-03

### Added

- Behavioral integration tests for tools, guards, state, handoff, configuration, and extension settings.
- Authenticated fake llama.cpp-compatible server for readiness, chat, failure, and doctor tests.
- Isolated install smoke covering `lai version`, `lai status`, and `lai doctor` in a synthetic repository.
- Public TOML configuration with explicit CLI, environment, file, and default precedence.
- Real VSIX packaging and archive-content inspection gate.

### Changed

- Added the `lai` command wrapper and isolated-install server helpers.
- Made skills, state, metrics, audit, server launcher, llama-server, and chat-template paths configurable.
- Recognize `python -m unittest` as a successful validation command.

### Security

- Added regression tests for traversal, symlinks, overwrite refusal, Git inspection, shell denylist, API authentication, and publication scanning.
- Direct Git mutations through guarded shell execution are blocked while tested inspection commands remain available.

## [0.3.0] - 2026-09-03

### Added

- First public-source extraction of the LAI local coding agent.
- Fourteen VS Code chat commands and eight mode skills.
- Batch inspection and transactional exact-replacement patching.
- Validation, acceptance, evidence, debug-evidence, and post-patch sanity guards.
- Workspace handoff, metrics, and forensic audit JSONL.
- Synthetic smoke tests, portable configuration, and public documentation.

### Changed

- Model, host, port, data directory, API-key path, and extension agent path are configurable.
- Windows/WSL launchers no longer contain machine-specific user paths.
- Public extension identifiers no longer contain a personal publisher name.
- Model-server readiness probes use the configured Bearer authentication.

### Security

- Real keys, logs, state, handoffs, metrics, audits, models, and historical backups are excluded.
- Security documentation explicitly distinguishes repository path confinement from shell sandboxing.

## [0.2.3] - 2026-09-03

Historical private-development baseline from which the public extraction was made. It is documented for provenance but was not published as a public release.
