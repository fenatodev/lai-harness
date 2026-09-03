# Changelog

All notable changes to this project are documented here.

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
