# Changelog

All notable changes to this project are documented here.

## [0.4.0-alpha.5] - 2026-09-03

### Fixed
- Route early `--plan` completions through the deterministic final synthesis instead of returning an intermediate draft.
- Preserve the preloaded project snapshot as evidence during final plan synthesis.
- Add regression coverage for plan-finalizer bypass and existing truncation recovery behavior.

## [0.4.0-alpha.4] - 2026-09-03

### Added

- Added a guarded `rewrite` tool for replacing the full contents of an existing file after complete inspection, with stale-content detection, repository confinement, symlink refusal, atomic replacement, and file-mode preservation.
- Added deterministic Python syntax checking to post-write sanity validation.

### Changed

- Detect `finish_reason=length`, discard incomplete assistant generations, and retry once per round with a larger bounded token budget instead of reusing truncated output.
- Increase the forced write-phase generation budget to reduce incomplete large edits while keeping normal implementation rounds compact.
- Make blocking post-write sanity deterministic rather than using an additional model completion as a code-review judge.
- Run post-write sanity after both transactional patches and guarded full-file rewrites.

### Fixed

- Prevent immediate validation laundering after an assertion failure by requiring a non-test implementation repair before allowing test expectations to be changed.
- Allow legitimate test correction after the implementation has been repaired and revalidated but the assertion still fails.

### Tests

- Added regression coverage for truncated-response recovery, repeated truncation failure, per-round retries, and adaptive write-phase token budgets.
- Added regression coverage for guarded rewrites, stale-file refusal, symlink refusal, full-file inspection requirements, executable-mode preservation, and Python syntax sanity.
- Added regression coverage for source-first assertion repair while preserving legitimate syntax and expectation corrections in tests.

## [0.4.0-alpha.3] - 2026-09-03

### Fixed

- Honor an exact validation command explicitly requested by the user with `valide apenas/somente com:` or `validate only with:` after a successful write.
- Prevent post-write validation loops when the requested verification command is intentionally narrower than LAI's built-in test, lint, compile, and build validators.

### Tests

- Added regression coverage proving that an explicitly requested verification command can complete a write flow.
- Added regression coverage proving that an unrequested `cat` command still cannot bypass the normal validation guard.

## [0.4.0-alpha.2] - 2026-09-03

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
