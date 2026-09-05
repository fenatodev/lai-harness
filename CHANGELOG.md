## [0.4.0-beta.23] - 2026-09-05

### Added
- Added deterministic freshness validation for persisted update-triage evidence using LAI version and update-source manifest SHA-256.
- Added `refresh_required` plus explicit stale-evidence reason codes and an operator-only refresh command.

### Safety and correctness
- Stale snapshots suppress all old per-source recommendations rather than presenting them as current actions.
- Triage remains offline/model-free and never performs its own remote refresh.
- Fresh snapshots preserve beta.22 security-first triage behavior unchanged.
- Completed spec 021 is now marked complete in its retained traceability document.

### Dogfood
- A real beta.22 snapshot under a beta.23 runtime produced `refresh_required`; one explicit remote check converged the evidence and restored normal triage without source mutation.

## [0.4.0-beta.22] - 2026-09-05

### Added
- Added local-only `lai update triage` to rank the latest persisted update observation without network or model calls.
- Added deterministic security, compatibility, visibility, maintenance, managed, reference, and current priorities with explicit urgency/action/reason codes.
- Added patch/minor/major/revision version-scope classification for comparable numeric versions.

### Safety and maintenance
- Known vulnerabilities outrank all ordinary maintenance signals; release-note prose is excluded from triage inputs and output.
- Incomparable runtime version schemes remain manual compatibility review rather than guessed upgrades.
- `lai update` still exposes no apply/install/download/upgrade/commit/push/merge/tag/PR/publication authority.
- Updated Harness Score from 1.6.3 to 1.6.4 after both versions produced the same L4 / 100/108 result with successful exits.
- Synchronized Harness Score 1.6.4 across Makefile, exact v1.6.4 Action SHA, update manifest, verification workflow, and current development docs.

### Validation
- Focused triage/pin regressions green; Harness Score 1.6.4 remains L4 at 100/108 (93%).
- Full local gates: 243 tests + 85 pytest subtests; strict mypy green; publication scan clean; VSIX inspection passed.

## [0.4.0-beta.21] - 2026-09-05

### Added
- Added `lai update plan`, explicit `lai update check --remote`, and local `lai update latest` for bounded maintenance intelligence.
- Added a versioned trusted-source manifest covering Python development sensors, Harness Score, llama.cpp, Dependabot-managed GitHub Actions, and selected reference-agent upstreams.
- Added PyPI exact-version vulnerability evidence, latest-version comparison, upstream release provenance, bounded release-note excerpts, SHA-256 hashes, and change-since-last-check tracking.
- Added installed-manifest synchronization under `$LAI_DATA_DIR/update-intelligence`.

### Safety and architecture
- Update intelligence uses fixed official HTTPS metadata hosts, GET-only requests, no redirects, bounded response/time limits, and no public-feed credentials.
- Upstream release-note text is untrusted evidence and is never executed or injected as instructions.
- There is no apply/install/download/upgrade/PR/merge/tag/publish operation; detected candidates must enter the normal spec/branch/validation flow.
- llama.cpp build ids and semver release tags are treated as incompatible schemes requiring manual compatibility review rather than fake ordinal comparison.
- Ruff now explicitly lints the extensionless `src/local-agent`, closing a sensor gap discovered while hardening this cut.

### Dogfood evidence
- The first live check found mypy, pytest, and Ruff current; GitHub Actions managed by Dependabot; Harness Score `1.6.4` available over the pinned `1.6.3`; and reference-agent release observations without applying any change.
- A repeated live check reported unchanged upstream observations and preserved the source checkout.

### Validation
- Full local gates: 238 tests + 85 pytest subtests; strict mypy green; Harness Score L4 at 100/108; publication scan clean; VSIX inspection passed.

## [0.4.0-beta.20] - 2026-09-05

### Added
- Added `lai model run` with versioned disposable plan/debug/implement/review/security fixtures against the already-loaded authenticated local model.
- Added independent validation, objective claim/evidence mismatch detection, response evidence hashes/excerpts, and isolated metrics/audit capture.
- Added model/server/hardware and harness/fixture provenance, repeatable sampling, multi-file scoring, `latest` result resolution, and minimum sample coverage before a result is decision-eligible.
- Added installer synchronization for the canonical model-evaluation fixtures under `$LAI_DATA_DIR/model-eval`.

### Safety and architecture
- Evaluation never downloads, starts, stops, switches, fine-tunes, or automatically selects a model.
- Model-backed fixtures run only in disposable repositories and must preserve the source checkout HEAD/status.
- Live benchmark result JSONL remains local operational evidence rather than public-source state by default.
- The configured Ministral baseline remains unchanged until another candidate wins repeatable local tests.

### Evidence
- First manual bake-off: Ministral 3 8B Q4_K_M outperformed Qwen2.5-Coder-7B-Instruct Q4_K_M on the initial five-scenario sample, with Qwen showing false edit/test claims in `implement`.
- The automated runner subsequently caught a real repeated review miss from the Ministral baseline, demonstrating why repeated samples are required before model decisions.

### Validation
- Full local gates: 225 tests + 72 pytest subtests; strict mypy green; Harness Score L4 at 100/108; publication scan clean; VSIX inspection passed.

## [0.4.0-beta.19] - 2026-09-05

### Fixed
- Release packs now select the exact target-version section from `docs/RELEASE-NOTES.md` instead of reusing a stale legacy `Release body for GitHub` marker.
- Annotated-tag messages now derive from the same target release heading instead of a hardcoded historical title.
- Version-prefix matching is exact enough to prevent targets such as `beta.1` from matching `beta.10`.
- Current beta publishing/readiness/checklist documentation now describes the actual release scope.

### Safety and architecture
- No runtime authority, model behavior, persistence format, remote capability, Git authority, dependency, or control-plane behavior changes.

### Validation
- Focused release-pack/identity regressions and install smoke pass.
- Full local gates: 218 tests + 72 pytest subtests; strict mypy green; publication scan clean; VSIX inspection passed.

## [0.4.0-beta.18] - 2026-09-05

### Added
- Added version 1 machine-readable JSON Schema contracts for workspace state, metric events, audit events, and recovery checkpoints.
- Added configurable bounded retention for workspace state and metrics/audit JSONL through the existing CLI, environment, and TOML precedence.
- Added atomic tail pruning for metrics and audit files plus focused compatibility/retention regressions.

### Changed
- New workspace, metrics, and audit records now declare `schema_version: 1`; recovery checkpoints use the same runtime-record schema version.
- Legacy unversioned workspace/metric/audit records remain readable. Unsupported future metric/audit versions are skipped and unsupported workspace/checkpoint state fails closed.

### Safety and architecture
- Retention affects local observability/state records only and never repository files, safe workspaces, promoted worktrees, Git history, release artifacts, or model files.
- No new runtime dependency, model behavior, remote capability, Git authority, or release authority is introduced.

### Validation
- Focused runtime-record/config/state/checkpoint regressions pass.
- Full local gates: 217 tests + 72 pytest subtests; strict mypy green; publication scan clean; VSIX inspection passed.

## [0.4.0-beta.17] - 2026-09-05

### Changed
- Migrated GitHub-maintained CI actions to reviewed Node 24-compatible v7 releases pinned to immutable full commit SHAs.
- Publication packaging now uses explicit Node.js 24 and disables unnecessary setup-node package-manager caching.
- Added weekly Dependabot tracking for GitHub Actions so SHA updates arrive as reviewable pull requests.

### Safety and reproducibility
- Added regressions that reject floating official GitHub Action references and unreviewed official action dependencies.
- LAI runtime capabilities, model behavior, remote authority, promotion behavior, and runtime Python dependencies are unchanged.

### Motivation
- Removes the live GitHub Actions Node 20 deprecation warning observed during the beta.16 tag CI instead of pursuing unrelated Harness Score points.

### Validation
- Local disposable-env gates: Ruff green, strict mypy 0 issues, 209 pytest/unittest tests + 68 pytest subtests, publication scan clean, and VSIX inspection passed.

## [0.4.0-beta.16] - 2026-09-05

### Added
- Added a generated, version-pinned `requirements.txt` development-sensor lock sourced from `requirements-dev.in` while keeping the runtime standard-library-only.
- Added pinned mypy 2.3.1 with a strict ratchet over the Python development guardrail hooks.
- Added `make typecheck` and enforced static type checking in Python 3.11/3.12 CI and the publication gate.

### Changed
- Added explicit type annotations to shell-policy and feedback hooks without weakening fail-closed or repository-confinement behavior.
- CI now installs all development sensors from the canonical generated lock; `requirements-dev.txt` is a compatibility include only.
- Removed the completed workspace-promotion item from the near-term roadmap and corrected stale documentation that still described promotion as future work.

### Harness maturity
- Harness Score 1.6.3 improved from 93/108 (86%) to 100/108 (93%) while remaining L4 Self-correcting.
- Remaining score gaps are intentionally deferred: custom subagents require real delegation/orchestration, and MCP config requires the governed MCP broker boundary.

### Validation
- Strict mypy passes on the declared two-module guardrail scope with zero issues.
- Focused quality-sensor and development-hook regressions pass before the full release gate.
- Full local gates: 206 tests + 68 pytest subtests; publication scan clean; VSIX inspection passed.

## [0.4.0-beta.15] - 2026-09-05

### Added
- Added read-only promotion proposals for successful isolated work runs with complete patch SHA-256, changed paths, source baseline, and deterministic target branch.
- Added explicit hash-bound promotion into durable `lai/promotion-*` Git worktrees under the LAI data directory.
- Added repeated `full` Docker-sandbox validation immediately before promotion and exact post-apply patch-hash verification.
- Added idempotent same-hash promotion and structured promotion state/evidence on control-run records.

### Safety
- Failed/cancelled runs, dirty or drifted source checkouts, mutable workspace-metadata drift, hash mismatch, validation failure, unsafe/oversized patches, and pre-existing targets fail closed.
- The control server's pre-model source SHA/branch/clean baseline is authoritative; workspace metadata is only consistency evidence.
- Promotion never edits or switches the active checkout and does not commit, push, merge, tag, publish, run a shell command supplied by the caller, or call the model.
- Promotion worktrees are forced outside the active source checkout.

### Fixed
- Replaced human-formatted `git status --short` first-line parsing with structured NUL-delimited path inventory, fixing `Makefile` being reported as `akefile` during mobile work-run dogfooding.

### Validation
- Full local suites: 200 tests + 68 pytest subtests.
- Real Docker + Git smoke verified validation exit 0, exact hash equality before/after promotion, a durable feature worktree, and unchanged source HEAD/tree/status.

## [0.4.0-beta.14] - 2026-09-04

### Added
- Added isolated remote `implement`, `fix`, `refactor`, and `ci-fix` control runs.
- Added structured `validate` profiles (`test`, `check`, `lint`, `build`, `typecheck`, `full`) that select recognized project validation argv rather than caller/model shell text.
- Added per-run disposable safe workspaces and bounded Git status/changed-path/diff evidence.
- Added Docker validation sandboxing with no network, read-only root, dropped capabilities, `no-new-privileges`, bounded resources, no host home, and no Docker socket.
- Added sandbox-readiness reporting and fail-closed work scheduling without automatic image pulls.

### Safety
- Remote work never writes directly to the source checkout and never receives generic `bash` or Git mutation tools.
- Work runs are rejected before model execution when the validation sandbox is unavailable.
- Remote callers cannot choose executable, cwd, environment, Docker image/mount/network options, or arbitrary validation commands.
- Applying/promoting a returned work diff remains intentionally outside beta.14.

### Validation
- Full suites: 193 tests + 68 pytest subtests before release-documentation gates.
- Real Docker smoke verified blocked network, hidden host secrets, hidden Docker socket, and successful structured validation.
- End-to-end remote `implement` smoke verified isolated workspace mutation while the source checkout SHA/files stayed unchanged.

### Architecture
- The control plane now distinguishes source-repository write posture from disposable-workspace write capability.
- Private mobile clients can request meaningful implementation work while irreversible promotion remains a separate future approval boundary.

## [0.4.0-beta.13] - 2026-09-04

### Added
- Added explicit shell-free remote capability profiles separate from local mode tool sets.
- Added asynchronous remote `diagnose` and `release` while keeping their local CLI tool sets unchanged.
- Added lifecycle/status reporting for the `shell-free-read-only` profile and focused fake-model schema inspection tests.

### Safety
- Remote control children never receive `bash`, `edit`, `create`, `patch`, or `rewrite` schemas.
- Unsupported write-capable modes still fail before scheduling, and callers still cannot choose commands, executables, cwd, argv prefixes, or environment overrides.
- Local `bash` remains explicitly unsandboxed; beta.13 avoids exposing it remotely instead of making a stronger containment claim.

### Architecture
- Capability reduction now happens before model inference by intersecting local mode tools with a dedicated remote profile.
- `diagnose`/`release` remote utility no longer depends on trying to classify arbitrary shell as read-only.

## [0.4.0-beta.12] - 2026-09-04

### Added
- Added asynchronous authenticated control runs through `POST /v1/runs` for the shell-free `plan`, `review`, and `security` modes.
- Added `GET /v1/runs/<control_run_id>` lifecycle/result inspection and scoped `DELETE` cancellation for queued/running control runs.
- Added a single-worker bounded queue, fixed subprocess argv/cwd, bounded output capture, terminal-record retention, and shutdown cleanup.
- Added a real subprocess smoke against `FakeLlamaServer` proving remote model execution without repository mutation.

### Safety
- Remote run requests cannot choose an executable, shell command, argv prefix, cwd, or environment key; child launch uses `shell=False` and the current `local-agent` only.
- `diagnose` and `release` remain excluded from HTTP because their current `bash` surface can still allow shell redirection; they require a stronger structured read-only shell boundary first.
- Write-capable modes remain rejected before scheduling, and the control API still exposes no generic shell, Git mutation, file-write, package-install, or OS-administration endpoint.
- Submitted tasks are not persisted as a new control-plane transcript store; public records expose task length and bounded terminal output only.

### Architecture
- Model work is serialized intentionally because the local model is a single scarce resource.
- Beta.12 makes the control plane useful to a future Telegram/PWA gateway while keeping approval/write workflows deferred to a separate trust-boundary cut.

## [0.4.0-beta.11] - 2026-09-04

### Added
- Added `lai serve`, an authenticated loopback-only HTTP/JSON control plane implemented with the Python standard library.
- Added `lai control-token init|status` with a control-plane bearer token separate from the llama.cpp API key.
- Added read-only HTTP surfaces for status, readiness, public run summaries, and deterministic policy classification.
- Added focused control-plane tests plus installed-wrapper smoke coverage that starts the server and queries `/v1/status`.
- Added `docs/CONTROL-PLANE.md` and a semantic `local-control-plane` subsystem contract.

### Safety
- Control tokens are generated with cryptographic randomness, written mode `0600`, never printed by default, and not silently overwritten.
- `lai serve` rejects non-loopback binds in beta.11.
- The HTTP surface exposes no model execution, arbitrary shell/Git execution, repository writes, or release publication.
- JSON request bodies are bounded and malformed/media-type/method errors fail through structured responses.

### Architecture
- Recorded `lai-gateway` as a separate mobile transport project (Telegram first, then private PWA/Tailscale).
- Recorded a separate commercial-automation dogfood/product repository rather than expanding the coding harness into CRM/social automation.

## [0.4.0-beta.10] - 2026-09-04

### Added
- Added opt-in remote project handoff with separate local/offline and remote governance evidence.
- Added tag-target and `origin/main` integration evidence to deterministic release-check output.

### Changed
- Feature-branch release candidates now report `ready_for_integration`; `ready_to_tag` is reserved for synchronized `main`.
- Expected release tags that point to another commit now block release-check.
- Remote handoff uses verified GitHub governance as the effective status while retaining offline status for auditability.

### Safety
- Default handoff remains offline and model-free; remote handoff performs GitHub GET requests only.
- Offline release-check does not claim to prove GitHub CI completion; protected CI remains a separate release gate.


## [0.4.0-beta.9] - 2026-09-04

### Added
- Added deterministic `lai policy-check` so repository shell hooks can reuse the runtime `ALLOW` / `ASK` / `DENY` policy without executing the requested action.
- Added repository-local gate and feedback hooks under `.cursor/hooks/` plus an explicit `verify-change` workflow.
- Added a dedicated `Harness maturity` GitHub Actions workflow pinned to Harness Score v1 commit `7cf25e00af7336f0c6d0b5e69a6f0ca7f1b4553a` and gated at L4.
- Added focused hook/policy tests and L4 validation via `make harness-score-gate`.

### Changed
- Strengthened shell policy so force push, hard reset, npm publication, and recursive forced PowerShell deletion are deterministic `DENY` decisions.
- Extended remote release governance to require `Harness Score L4` alongside the existing product CI checks.
- Pinned local Harness Score measurement to 1.6.3 for reproducible maturity gates.

### Maturity
- Harness Score improved from L3 Sensing, 76/108 (70%) to L4 Self-correcting, 93/108 (86%).
- Remaining score gaps are not filled with decorative subagent, MCP, type-checker, or lockfile artifacts; those require separate product justification.


## [0.4.0-beta.8] - 2026-09-04

### Added
- Added opt-in `lai release-governance --remote` for read-only GitHub branch-protection and pre-release verification.
- Added SHA-256 comparison for an attached VSIX when GitHub exposes the asset digest.
- Added remote-governance unit coverage and `.specs/023-remote-release-governance.md`.

### Changed
- Verified GitHub actions now clear from `manual_actions`; missing or unverified state remains actionable.
- Updated the beta release workflow for protected `main`: feature branch, PR, CI, merge, then tag and pre-release.
- Updated current beta metadata and examples to `0.4.0-beta.8`.


## [0.4.0-beta.7] - 2026-09-04

### Added
- Added deterministic `lai project-handoff` / `lai next-chat` to render or write a portable next-chat project handoff.
- Added external handoff files: `PROJECT-HANDOFF.md`, `NEXT-CHAT-PROMPT.md`, and `summary.json`.
- Added project handoff documentation and validation coverage for chat migration.

### Changed
- Updated beta publishing docs, release notes, checklist, README examples and VS Code package metadata for `0.4.0-beta.7`.


## [0.4.0-beta.6] - 2026-09-04

### Added
- Added deterministic `lai release-governance` / `lai governance` for local release posture and manual GitHub publication actions.
- Added JSON release-governance output covering release-check phase, release-pack presence, branch-protection action and GitHub Release action.
- Added release governance documentation and validation coverage.

### Changed
- Updated beta publishing docs, release notes, checklist, README examples and VS Code package metadata for `0.4.0-beta.6`.


# Changelog
## [0.4.0-beta.5] - 2026-09-04

### Added
- Added deterministic `lai release-pack` / `lai release-pack --json` to generate local GitHub Release publication files without tagging, pushing, uploading, publishing, calling the model, or mutating repository files.
- Added optional `lai release-pack --with-vsix` packaging into the external release pack directory.
- Added release pack documentation and validation coverage for ready-to-paste release body, checklist, human-run commands and summary metadata.

### Changed
- Updated beta publishing docs, release notes, checklist, README examples and VS Code package metadata for `0.4.0-beta.5`.


## [0.4.0-beta.4] - 2026-09-04

### Added

- Added `lai workspace status`, `lai workspace create`, `lai workspace clone-smoke`, and `lai workspace clean` for disposable dogfood workspaces.
- Added safe workspace documentation and tests so write modes can be exercised away from `main` and release branches.

### Changed

- Updated beta release notes, checklist, publishing metadata, README examples, and VS Code package version for `0.4.0-beta.4`.

### Safety

- Safe workspace creation copies only tracked files into a standalone Git repository on `test/lai-smoke`.
- Cleanup refuses targets outside the configured safe workspace base.

All notable changes to this project are documented here.

## [0.4.0-beta.3] - 2026-09-04

### Added
- Add a protected-branch write guard that blocks `edit`, `create`, `patch`, and `rewrite` on `main`, `master`, and `release/*` unless explicitly overridden.
- Document safe disposable-branch smoke testing for write-capable modes.

### Changed
- Keep beta release posture focused on manual publication and deterministic safety gates.

### Tests
- Added regression coverage for protected branch write denial and explicit local override behavior.


## [0.4.0-beta.2] - 2026-09-04

### Changed
- Polish public release metadata, GitHub publishing notes, and beta release instructions after the first beta cut.
- Use `lai-harness` in generated VSIX artifact filenames while preserving extension compatibility identifiers.
- Update public quick-start and release-check examples for the beta.2 release target.

### Added
- Add ready-to-paste GitHub release notes and a human release checklist for the beta line.
- Add a traceable release-polish spec for the beta.2 stabilization cut.

### Tests
- Add regression coverage that publishing metadata, release notes, and package artifact names stay aligned with the public `lai-harness` identity.

## [0.4.0-beta.1] - 2026-09-04

### Changed
- Promote the harness from alpha to beta after the readiness, diagnostic skills, sanitized run export, and release preflight gates stabilized.
- Update public quick-start examples and release documentation for the beta.1 target.

### Added
- Document the beta.1 release posture, expected validation sequence, and remaining non-goals.
- Add a traceable beta-readiness spec for the first beta cut.

### Tests
- Keep the full local validation suite and isolated install smoke aligned with the beta.1 version.


## [0.4.0-alpha.21] - 2026-09-04

### Added
- Preload a deterministic release preflight context for release-mode runs with Git state, tags, readiness checks, and Makefile validation commands.
- Add model-free `lai release-check` / `lai release-check --json` for beta gates and release posture checks.
- Dispatch public CLI mode aliases such as `lai diagnose`, `lai ci-fix`, and `lai release` to their matching modes.
- Document release preflight behavior before beta readiness review.

### Changed
- Tighten release skill instructions so small local models prefer repository-defined validation commands over ad-hoc pytest/python probing.

### Tests
- Added regression coverage for release preflight content, deterministic release check, and installed public mode aliases.

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
