## lai harness v0.5.0 — post-A12 autonomy and public repository graduation

`v0.5.0` marks the post-A12 public graduation of lai harness. It packages the completed A0-A9 and A12 work, records A10/A11 only as experimental fixture contracts, and publishes the refreshed GitHub-facing documentation set. The release keeps the product local-first and conservative: fixture-only browser/MCP/external-action/trusted-host/computer-use surfaces remain fixtures, real credentials and real account effects remain disabled, and publication does not enable autoupdate or remote administration.

### Highlights

- Structured trajectory, aggregate budgets, scoped authority presets and durable approval intents.
- Verified sandbox executor, safe workspaces, sandbox primitives and hash-bound promotion boundaries.
- Local-chat/Gateway contract, inspector/review surfaces and Linux/WSL bootstrap diagnostics.
- Governed egress, fixture browser workflows, sandboxed fixture MCP execution and fake external-action adapter.
- Model capability profiles, capability-declared skills, session forks and bounded delegate waves.
- Distribution status diagnostics, uninstall preservation behavior and risk-proportional validation matrix.
- Public README refresh, documentation portal, architecture diagrams, sanitized CLI screenshots, contribution guidance and known limitations.

### Validation

Local release gate before tagging:

```bash
lai release-check --target 0.5.0 --json
make milestone-gate
```

### Deliberate non-goals

This release does not enable real credential delivery, real GitHub push/PR/merge/tag/release automation inside the harness, real browser automation, generic MCP `call-tool`, model downloads, cloud fallback, autoupdate, branch-protection changes or package-registry publication.

## lai harness v0.4.9 — model-evaluation evidence expansion

`v0.4.9` packages the next local-first reliability slice after `v0.4.8`: bounded planning evidence, safer diagnose behavior, design-only MCP allowlist evidence, and a stronger model-evaluation suite based on observed dogfood failures. It does not enable MCP tool execution, browser automation, mobile writes, Telegram/PWA integration, automatic dependency updates, model switching, learning/self-modification, commits, pushes, tags, releases, or remote resource mutation.

### What changed

- Added `plan-validation-command-grounding`, a read-only model-evaluation fixture derived from observed Qwen dogfood where a candidate recommended unavailable `pytest` validation in a stdlib-only repository.
- Expanded required model-backed decision eligibility from five scenarios to six, so older repeated baseline records remain historical support rather than fresh decision-eligible evidence under the expanded suite.
- Added forbidden output-pattern checks for validation/tool recommendations such as `pytest` and `pip install` in fixtures that intentionally expose only stdlib `unittest` validation.
- Recorded `refusal_flags` and refusal reasons separately from hallucination flags so quality review can distinguish generic disclaimers/refusals from unsupported edit, validation, or line-reference claims.
- Preserved Ministral as the local baseline until another <=8 GiB candidate beats it with repeated, decision-eligible evidence across the expanded required scenario set.
- Added M3 MCP allowlist design evidence for a future narrow `repo_public_text_read` class while keeping MCP `call-tool` denied and non-executing.
- Kept M1 structured-context dogfood and diagnose hardening in the release scope: compact active-spec context, minimal active-spec receipts, deterministic diagnose preflight for simple status requests, strict chat-template history normalization, and bounded model API error reporting.

### Safety boundary

- The release is evidence hardening, not an authority expansion.
- MCP `call-tool` remains denied by default.
- Model-evaluation records remain bounded and secret-free.
- The default model remains Ministral; Qwen or any other candidate must win repeated local evidence before adoption.
- Release tooling still performs no tag, merge, push, upload, publication, or GitHub mutation by itself.

### Validation gate

```bash
make milestone-gate
```

Local milestone evidence: Ruff passed; pytest passed with 325 tests and 144 subtests; Harness Score passed at L4 103/108; `validate.sh` passed with 325 unittest tests, strict mypy over seven source files, generalized publication scan, package generation, and VSIX inspection green in 162.63s. A focused dogfood run of `plan-validation-command-grounding` against the current Ministral endpoint passed with score 100.0, three tool calls, no refusals, no hallucinations, and no changed paths; because the source tree was dirty during that run, it is focused fixture evidence rather than final decision-eligible model-selection evidence.

### Release commands

```bash
lai release-check --target 0.4.9 --json
lai release-pack --target 0.4.9 --with-vsix --json
lai release-governance --target 0.4.9 --remote --json
lai project-handoff --target 0.4.9 --remote --json
```

## lai harness v0.4.8 — context intelligence and operating policy

`v0.4.8` improves day-to-day development quality for constrained local models by packaging deterministic context-intelligence views and a codified operating-mode policy. It does not enable shell authority for remote read-only profiles, MCP tool execution, browser automation, dependency updates, model switching, commits, pushes, tags, releases, or remote resource mutation.

### What changed

- Added `lai operating-mode` and `docs/OPERATING-MODE.md` so local-first milestone batching, delayed release ritual, read-only external evidence, product-progress gates, and capability-based compatibility are inspectable without contacting the model.
- Added `lai context map` for metadata-only repository structure, manifest, changed-path, directory/suffix, and semantic-subsystem orientation.
- Added `lai context changes` and `lai context diff` for compact Git status, shortstat, and per-file addition/deletion counts without raw hunks.
- Added `lai context checks` for Makefile target names, validation profile names, test inventory, and suggested feedback loops without reading recipes or executing commands.
- Added `lai context runs` for recent run/process and recovery-checkpoint metadata without stdout, stderr, task text, transcripts, failure reasons, workspace paths, file contents, or raw diffs.
- Added `lai context symbols <path>` for bounded Python/JavaScript function, class, and method navigation metadata without source bodies.
- Exposed the same metadata views through the shell-free structured `context` tool for local and remote modes, and injects compact map/change summaries into context-intelligence modes to reduce early repository-discovery overhead.
- Counts the structured `context` tool as read-only exploration so repeated metadata probing cannot bypass pre-write progress guards.

### Safety boundary

- Context views are advisory metadata only; files and diffs still must be inspected before relying on implementation behavior.
- The context tool does not expose raw file bodies, raw diffs, stdout, stderr, transcripts, model keys, local credentials, private paths, Makefile recipes, or test bodies.
- Operating-mode policy is inspectable guidance and does not add release, GitHub, dependency-management, model-lifecycle, browser, MCP execution, or remote-write authority.

### Validation gate

```bash
make milestone-gate
```

Local milestone evidence: Ruff passed; pytest passed with 311 tests and 144 subtests; Harness Score passed at L4 100/108; `validate.sh` passed with 311 unittest tests, strict mypy over seven source files, generalized publication scan, and VSIX inspection green in 167.65s. Gateway stack compatibility also passed from `lai-gateway` 0.1.34 against this checkout with Harness `0.4.8 >= 0.4.6`, contract compatibility ok, MCP foundation non-executing, and `overall=ready_for_local_commit`.

### Release commands

```bash
lai release-check --target 0.4.8 --json
lai release-pack --target 0.4.8 --with-vsix --json
lai release-governance --target 0.4.8 --remote --json
lai project-handoff --target 0.4.8 --remote --json
```

## lai harness v0.4.7 — control-run event timeline

`v0.4.7` improves progress observability for the Gateway and other polling clients by enriching control-run event timelines with metadata-only execution milestones. It does not enable shell authority, write-capable Gateway runs, MCP tool execution, browser automation, downloads, commits, pushes, tags, releases, or remote resource mutation.

### What changed

- `GET /v1/runs/{control_run_id}/events` now reports bounded milestones beyond `queued`, `started`, and `finished` when the run record has the relevant evidence.
- New metadata-only milestones cover session context loading, isolated workspace preparation, child process start, bounded output capture, workspace result collection, and session persistence.
- Control-run records now keep timestamp metadata for these milestones so UI clients can show more useful progress without reading stdout, stderr, task text, transcripts, file contents, workspace paths, or raw diffs.
- The roadmap now treats `lai harness` v0.4.6 plus `lai-gateway` v0.1.33 as the stable integration baseline before further autonomy expansion.

### Safety boundary

- Event payloads remain metadata-only.
- The timeline reports counts and booleans such as `changed_path_count`, `output_truncated`, `diff_truncated`, and `session_persisted`, not sensitive content.
- No control-plane authority is expanded in this release.

### Validation gate

```bash
make milestone-gate
```

Release validation must pass after the version bump and before publication.

### Release commands

```bash
lai release-check --target 0.4.7 --json
lai release-pack --target 0.4.7 --with-vsix --json
lai release-governance --target 0.4.7 --remote --json
lai project-handoff --target 0.4.7 --remote --json
```

## lai harness v0.4.6 — stable recovery rollback

`v0.4.6` hardens the runtime recovery path into an operator-usable rollback boundary. It adds checkpoint inspection, private pre-write snapshots, hash-checked rollback, atomic restore, snapshot schema coverage, installed dogfood, and cleanup of abandoned rollback content.

### What changed

- Added `lai checkpoint list/show` for deterministic recovery-checkpoint inventory without model access.
- Added private pre-write snapshot capture under `$LAI_DATA_DIR/snapshots` plus `lai snapshot show` metadata output that does not print captured file content.
- Added `lai rollback <run-id|--last>` with `--dry-run` and `--json` support.
- Rollback requires the active checkpoint for the same run and blocks when current file hashes differ from checkpoint evidence.
- Rollback restores captured UTF-8 file content atomically and deletes files that were created by the run when the pre-write snapshot proves they did not exist.
- `lai recovery clear` now removes the associated pre-write snapshot as well as the recovery checkpoint, so stale rollback content is not left behind after abandoned recovery state.
- Added `schemas/runtime/snapshot.schema.json` and documented snapshot records as versioned runtime state.
- Added authenticated `GET /v1/runs/{control_run_id}/events` for polling clients to display bounded metadata-only progress without reading stdout, stderr, task text, or transcripts.
- Updated the roadmap to keep stability, rollback, trust, and context quality ahead of MCP/browser authority expansion.

### Safety boundary

- Rollback does not use `git reset`, mutate `.git`, replay prior tool calls, contact the model, push, tag, publish, or touch remote resources.
- Snapshot CLI output is metadata-only and intentionally omits captured file content.
- Rollback fails closed if the checkpoint is missing, belongs to another run, has malformed hashes, lacks a snapshot, or current file hashes drift from the recorded checkpoint state.
- Snapshot and recovery state remain outside the repository and are removed together by `lai recovery clear`.

### Validation gate

```bash
make milestone-gate
```

Local milestone evidence: Ruff passed; pytest passed with 295 tests and 144 subtests; Harness Score passed at L4 100/108; `validate.sh` passed with 295 unittest tests, strict mypy over seven source files, generalized publication scan, and VSIX inspection green.

Installed rollback dogfood covers agent-driven write, checkpoint discovery, private snapshot metadata, rollback dry-run, rollback apply, drift blocking, and recovery cleanup of associated snapshots.

### Release commands

```bash
lai release-check --target 0.4.6 --json
lai release-pack --target 0.4.6 --with-vsix --json
lai release-governance --target 0.4.6 --remote --json
lai project-handoff --target 0.4.6 --remote --json
```

## lai harness v0.4.5 — MCP broker foundation

`v0.4.5` adds the first governed MCP broker boundary. It discovers and validates repository-local MCP config files, reports declared servers, and exposes non-executing MCP policy checks without starting external MCP servers or granting tool-call authority.

### What changed

- Top-level `lai --help` now lists the existing status, recovery, observability, spec, semantic, and workspace surfaces so operators do not need to discover them by reading source.
- Core CLI subcommands now use deterministic successful help output instead of treating `--help` as an error or running status commands.
- `lai recovery clear` now discards stale interrupted checkpoints explicitly, without repository mutation or model access.
- Mode commands such as `lai plan --help`, `lai review --help`, and `lai implement --help` now print deterministic usage without invoking the model.
- Top-level `lai --help`, `lai -h`, and `lai help` now print deterministic command usage without invoking the model.
- `lai web search` and `lai web fetch` provide direct bounded CLI dogfood for the existing read-only public web evidence tools, without browser actions or stateful web access.
- Added `lai mcp status`, `lai mcp tools`, and `lai mcp policy-check`.
- Added `lai mcp --help`, `lai mcp help`, and subcommand help as successful non-executing help output.
- Added authenticated `GET /v1/mcp/status`, `GET /v1/mcp/tools`, and `POST /v1/mcp/policy-check` control-plane routes.
- `GET /v1/runs?limit=N` now lists control-plane run records with `control_run_id`, while local `lai runs` remains the historical observability view.
- Added MCP config discovery for `.cursor/mcp.json`, `.mcp.json`, and `.agents/mcp_config.json` using `mcpServers` or `servers` maps.
- Added credential-shaped env validation: values for keys such as `TOKEN`, `API_KEY`, `SECRET`, `PASSWORD`, and `AUTH` must use `${ENV_VAR}` interpolation.
- Added secret-free output that lists env key names but never env values.
- Added strict MCP subcommand argument handling so unknown `status`/`tools` flags fail instead of being silently ignored.
- Generalized publication/VSIX scans and `.gitignore` coverage for private paths, known local IPs, and local runtime/build artifacts.
- Gateway-contract regression coverage now asserts the full run/session route set consumed by `lai-gateway`, including list and read endpoints.
- Added policy behavior that allows read-only non-executing status/list checks and denies `call-tool` execution in this foundation milestone.

### Safety boundary

- Release-pack command files and summary metadata omit the operator's local checkout path from release-facing artifacts.
- No MCP server is started.
- No MCP tool is executed.
- No environment variable value, credential file, control token, model key, shell authority, Git mutation, PR, tag, release, or remote resource mutation is exposed.
- Literal credential-shaped MCP env values block the config and are redacted from output.
- Publication and VSIX packaging gates reject private local paths and known local network IPs before release artifacts are accepted.

### Validation gate

```bash
make milestone-gate
```

Local milestone evidence: Ruff passed; pytest passed with 292 tests and 143 subtests; Harness Score passed at L4 100/108; `validate.sh` passed with 292 unittest tests, strict mypy over seven source files, generalized publication scan, and VSIX inspection green.

### Release commands

```bash
lai release-check --target 0.4.5 --json
lai release-pack --target 0.4.5 --with-vsix --json
lai release-governance --target 0.4.5 --remote --json
lai project-handoff --target 0.4.5 --remote --json
```

## lai harness v0.4.4 — control-session lifecycle

`v0.4.4` adds bounded lifecycle control for repository-scoped persistent sessions. It is driven by gateway dogfood: mobile/private clients can now create, inspect, and delete stale LAI sessions without gaining shell, Git, source-checkout, model-management, commit, push, PR, tag, or release authority.

### What changed

- Added authenticated `DELETE /v1/sessions/{session_id}` to remove one persistent control session for the currently served repository.
- Added local `lai sessions`, `lai sessions show <session-id>`, and `lai sessions delete <session-id>` commands for deterministic session cleanup without starting the control plane.
- Added typed session deletion with repository ownership checks, invalid-id rejection, symlink rejection, and secret-free public records.
- Updated the gateway contract, control-plane docs, README, and project handoff examples for the new session lifecycle boundary.
- Hardened `scripts/ministral-start` for reboot recovery by auto-discovering the checkout-local Windows launcher, converting the key-file path for PowerShell, locating `llama-server.exe`, and refusing to print key material.

### Safety boundary

- Session deletion removes only the matching repository-scoped session JSON record outside the source checkout.
- It does not delete runs, metrics, audit events, workspaces, source files, Git branches, tags, releases, model files, or remote resources.
- The new CLI commands are local, deterministic, model-free, and do not read or print API keys.

### Local model dogfood evidence

A one-repeat local model-evaluation run against a user-supplied Qwen2.5-Coder 7B Q4_K_M GGUF completed all five required scenarios but is not decision-eligible for a default-model switch: average score 55.4/100, with planning passing, debug and implementation failing, and review/security only partial. The result supports keeping the current default until another small local model wins on correctness and validation, not just availability.

### Release commands

```bash
lai release-check --target 0.4.4 --json
lai release-pack --target 0.4.4 --with-vsix --json
lai release-governance --target 0.4.4 --remote --json
lai project-handoff --target 0.4.4 --remote --json
```

## lai harness v0.4.3 — runtime startup hardening

`v0.4.3` packages the Windows/WSL llama.cpp startup hardening needed for repeatable local-model operation with the companion gateway. It keeps the Harness control-plane boundary unchanged while making the authenticated model-server launcher safer and more useful for local GGUF files.

### What changed

- Hardened `scripts/ministral-start` and `scripts/ministral-doctor` so authenticated `/props` probes read the llama.cpp key from file without placing the key in shell `curl` arguments.
- `scripts/ministral-start` now accepts an already-running authenticated model server without requiring `LAI_WINDOWS_LAUNCHER`; the launcher variable is needed only when a new Windows process must be started.
- `scripts/start-secure.ps1` accepts local GGUF paths through `LAI_MODEL`, keeps Hugging Face `-hf` fallback for model identifiers, exposes `LAI_CTX_SIZE`, `LAI_GPU_LAYERS`, and `LAI_PARALLEL`, and requires `--api-key-file` support instead of falling back to `--api-key`.
- Documented the validated small local-code path using a Windows-hosted Qwen2.5-Coder GGUF server with 4096 context and CPU layers.

### Safety boundary

- No model download, public bind, token printing, generic shell authority, commit, push, merge, tag, release publication, gateway route, or remote-write authority was added.
- The PowerShell launcher now fails closed when `llama-server` lacks `--api-key-file`; it no longer falls back to placing the key value in process arguments.

### Release commands

```bash
lai release-check --target 0.4.3 --json
lai release-pack --target 0.4.3 --with-vsix --json
lai release-governance --target 0.4.3 --remote --json
lai project-handoff --target 0.4.3 --remote --json
```

## lai harness v0.4.2 — gateway contract manifest

`v0.4.2` packages the gateway contract boundary for companion mobile/private-client work. It does not ship `lai-gateway` itself; it gives that separate project a stable machine-readable contract instead of forcing endpoint assumptions to be copied from prose.

### What changed

- Added `lai gateway-contract --json` for deterministic local discovery of the companion-gateway contract.
- Added authenticated `GET /v1/gateway-contract` to the loopback control plane.
- Added `schemas/runtime/gateway_contract.schema.json` and `docs/GATEWAY-CONTRACT.md`.
- Documented supported control-plane routes, bearer-auth expectations, request/run/session limits, run modes, companion responsibilities, and explicit forbidden capabilities.

### Safety boundary

- No Telegram, PWA, Tailscale, OAuth, webhook, notification, or messaging dependency was added to `lai-harness`.
- No generic remote shell, direct source-checkout write, dependency installation, commit, push, merge, PR, tag, release-publication, browser automation, JavaScript execution, direct llama.cpp proxy, or token disclosure authority was added.
- The endpoint is bearer-authenticated and does not include control tokens, model API keys, secret file contents, host environment variables, private run transcripts, or persistent-session turn bodies.

### Release commands

```bash
lai release-check --target 0.4.2 --json
lai release-pack --target 0.4.2 --with-vsix --json
lai release-governance --target 0.4.2 --remote --json
lai project-handoff --target 0.4.2 --remote --json
```

## lai harness v0.4.1 — operational capability patch

`v0.4.1` packages the first post-stable operational increment after `v0.4.0`. It adds practical remote-session continuity, bounded read-only web evidence for research workflows, and removes observed duplicate CI work without loosening release governance or model authority.

### What changed

- Scoped the main CI workflow so feature branches with pull requests are validated by the PR workflow without an extra generic branch-push CI run; `main` and `v*` release tags still run CI.
- Added persistent authenticated control-plane sessions backed by bounded, atomic, versioned files under the LAI data directory.
- Session-bound runs receive only compact, clearly untrusted historical context; unknown sessions fail before child process spawn, and persistence failures are visible.
- Added `web_search` and `web_fetch` evidence tools for selected research modes.
- Added `src/lai_web.py`, bounded SSRF-resistant public HTTPS fetch/search evidence, DuckDuckGo Lite search parsing, semantic navigation, install support, and strict mypy coverage.

### Safety boundary

- No model download, model switch, dependency install, generic remote shell, commit, push, merge, tag, or release-publication authority was added.
- Web evidence is HTTPS `GET` only, port 443 only, no credentials, no cookies, no caller-defined headers/body, no redirects, no browser automation, no JavaScript execution, no forms, and no file downloads.
- DNS answers must be globally routable; the TLS socket connects to one validated public IP while authenticating the original hostname.
- External web text is marked `untrusted_external_content=true` and cannot override user instructions, specs, policy, repository evidence, or safety boundaries.
- Remote write-capable profiles and release mode do not receive web tools in this release.

### Validation gate

```bash
lai readiness --json
lai release-check --target 0.4.1 --json
make milestone-gate
```

Pre-freeze local evidence: focused mocked web/network tests, install/control/quality regressions, bounded live public fetch/search dogfood, 271 pytest tests + 97 subtests, 271 unittest tests, strict mypy over seven files, Harness Score L4 100/108 (93%), publication scan, and VSIX inspection green.

## lai harness v0.4.0 — stable core graduation

`v0.4.0` freezes the first stable lai harness core after the beta stabilization line. The release keeps the local-first authority boundary intact while consolidating typed runtime boundaries, deterministic stable-release governance, faster non-redundant milestone validation, and repeated baseline-model evidence.

### What changed since beta.24

- Extracted configuration and spec-workflow logic into typed `src/lai_config.py` and `src/lai_specs.py`, following the beta.24 semantic-module pattern without changing public behavior.
- Added channel-aware release governance so plain semantic versions require GitHub `prerelease=false`, while alpha/beta/rc targets continue requiring pre-release metadata.
- Added `docs/STABLE-READINESS.md` as a finite graduation gate so deferred PWA/web/MCP/subagent/marketplace/signing work cannot silently block the stable core.
- Added `make milestone-gate`, which keeps Ruff, pytest, Harness Score, unittest, strict mypy, publication scan, static checks, and VSIX inspection while avoiding intentional duplicate runs of the same expensive evidence.
- Fixed persisted model-evaluation basename resolution after dogfood exposed that `lai model score first.jsonl second.jsonl` could choose a nonexistent repository path before the configured result directory.

### Operational evidence

- `lai readiness --json` reports `ready` with authenticated model-server health (`unauthenticated=401`, `authenticated=200`).
- The current Ministral baseline has 10 persisted records covering all five model-backed scenarios with at least two samples per scenario and is decision-eligible at 90.8/100 aggregate score.
- The repeated weak point remains `review-supported-findings` (55/100 twice, validation failed); the harness exposes that failure instead of treating it as success, so the default model remains unchanged rather than being promoted by optimistic prose.
- The final pre-freeze `make milestone-gate` completed in 125.29s with 255 pytest tests + 85 subtests, 255 unittest tests, strict mypy over five files, Harness Score L4 100/108 (93%), publication scan, and VSIX inspection green.

### Safety boundary

- No remote generic shell, automatic model/dependency/update apply, commit, push, merge, tag, or release-publication authority was added.
- Model-evaluation results remain local operational evidence and do not auto-select or download models.
- Historical beta release evidence remains unchanged; this entry defines the stable candidate only.

### Local freeze gate

```bash
lai readiness --json
lai release-check --target 0.4.0 --json
make milestone-gate
```

The GitHub release must be created only after protected-main integration and tag CI, with `draft=false`, `prerelease=false`, and the frozen VSIX digest verified by remote governance.

## lai harness v0.4.0-beta.24 — semantic contract modularization

This beta starts the planned monolith reduction with a deliberately low-risk deterministic boundary. Semantic code-contract data, rendering, and semantic-reference matching now live in a dedicated typed module while the public CLI and ranking behavior remain compatible.

### What changed

- Added `src/lai_semantics.py` with typed semantic subsystem/contract structures.
- Moved semantic contract rendering and semantic-reference matching out of `src/local-agent`.
- Added `semantic-code-contracts` as a canonical subsystem pointing at the extracted module.
- Updated the dependency-free local installer to deploy the module beside the runtime entrypoint.
- Expanded `mypy --strict` to include the extracted runtime module while retaining the existing guardrail-hook ratchet.
- Added source-tree, installed-runtime, semantic-ranking, and quality-sensor regressions for the new boundary.

### Safety boundary

- No policy decision, tool permission, model behavior, network request, control-plane capability, Git mutation path, or release authority changes in this cut.
- The extracted module remains Python-standard-library-only and deterministic.
- This is incremental modularization, not a broad rewrite of the runtime.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.24 --json
lai semantics --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

## lai harness v0.4.0-beta.23 — update evidence convergence

This beta hardens the beta.22 maintenance triage after real dogfooding exposed a stale-evidence edge case across local upgrades. Persisted observations from an older LAI or update-source baseline can no longer be presented as current maintenance advice.

### What changed

- Added deterministic snapshot freshness checks using the persisted LAI version and update-source manifest SHA-256.
- Added `overall=refresh_required` with explicit reason codes when the local baseline changed or legacy metadata is missing.
- Stale snapshots suppress old per-source security, compatibility, maintenance, managed, and reference actions instead of reinterpreting them as current.
- The only recovery action is the explicit operator command `lai update check --remote`; triage never refreshes itself.
- Fresh matching snapshots preserve beta.22 security-first ordering and compatibility behavior unchanged.
- Closed the stale textual `active` marker on completed release-governance spec 021.

### Dogfood evidence

After bumping the development runtime from beta.22 to beta.23 while retaining the beta.22 persisted snapshot, `lai update triage --json` returned `refresh_required` and only `refresh_update_evidence`. After one explicit `lai update check --remote`, the snapshot converged to beta.23 and normal triage resumed with the existing llama.cpp compatibility review intact.

### Safety boundary

- Freshness evaluation is local-only, deterministic, and model-free.
- No TTL, automatic network request, dependency apply, model update, Git mutation, PR, tag, or publication authority was added.
- Release-note prose remains excluded from freshness and priority decisions.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.23 --json
lai update triage --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

## lai harness v0.4.0-beta.22 — update triage

This beta turns the beta.21 maintenance radar into deterministic local triage. LAI can now distinguish a security problem from compatibility review, routine maintenance, managed dependencies, and informational upstream changes without granting itself update authority.

### What changed

- Added `lai update triage` / `--json`, which reads only the latest persisted update snapshot.
- Added structured priority, urgency, recommended action, reason codes, and change scope.
- Known vulnerability evidence is always prioritized ahead of routine version updates.
- Comparable numeric versions are classified as patch, minor, major, revision, or unchanged; incompatible schemes remain manual review.
- Release-note text is explicitly excluded from triage decisions and from the triage payload.
- Updated Harness Score from 1.6.3 to 1.6.4 after a same-repository equivalence run preserved L4 / 100/108 (93%) and exit 0.
- Pinned the Harness Score GitHub Action to exact v1.6.4 commit `d37e35060a77ba7665157125c809b826ce3b41ce` rather than a floating major tag.

### Safety boundary

- `triage` is offline/model-free and does not persist a second derived authority state.
- No candidate can be downloaded, installed, applied, committed, pushed, merged, tagged, published, or converted into a PR by `lai update`.
- Upstream prose remains untrusted evidence; only structured beta.21 metadata can influence triage.

### Why this matters

Long-lived update intelligence needs judgment, not just notifications. A vulnerability should interrupt normal maintenance; a patch such as Harness Score 1.6.4 can wait for a reviewed maintenance cut; a reference-agent release may be worth studying but should not become a dependency. This cut makes that distinction deterministic and dogfoods the first candidate through the same spec/CI/release path as any other change.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.22 --json
lai update triage --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

## lai harness v0.4.0-beta.21 — update intelligence

This beta adds a bounded maintenance radar that can observe trusted dependency, runtime, and reference-agent metadata without becoming an updater. It turns upstream change into audit-ready evidence for a later governed spec/PR.

### What changed

- Added deterministic offline `lai update plan` and explicit networked `lai update check --remote`.
- Added local `lai update latest` backed by atomically persisted versioned observations under `$LAI_DATA_DIR/update-intelligence`.
- Added official PyPI version and exact-pinned-version vulnerability checks for development sensors.
- Added Harness Score version observation, Dependabot-managed GitHub Actions status, and authenticated local llama.cpp build evidence.
- Added latest-release observation for Codex, Claude Code, Qwen Code, Kimi Code, and Hermes Agent as reference-only engineering signals.
- Added change-since-last-check tracking, SHA-256 provenance, bounded upstream release-note excerpts, and canonical source URLs.
- Updated Ruff/CI to lint the extensionless `src/local-agent` explicitly.

### Safety boundary

- Remote checks require explicit `--remote` and use only fixed official HTTPS metadata hosts.
- Redirects, arbitrary URLs, oversized/non-JSON responses, and public-feed credentials are rejected.
- Upstream release-note text is marked untrusted and never executed or treated as instructions.
- No model, dependency, skill, package, Git ref, PR, merge, tag, or release is changed automatically.
- llama.cpp build ids that cannot be ordered against release semver are flagged for compatibility review instead of being called upgrades.

### Why this matters

A long-lived coding harness must keep learning about ecosystem changes without surrendering its trust boundary. This cut separates awareness from authority: LAI can notice a security fix or useful upstream capability, but adoption still requires a focused spec, isolated validation, review, and protected integration.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.21 --json
lai update plan --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

## lai harness v0.4.0-beta.20 — automated model evaluation

This beta turns the existing model rubric into a repeatable local evaluation runner for the model already loaded behind the authenticated LAI endpoint. It measures coding-agent behavior on disposable fixtures without changing the configured default model or expanding runtime authority.

### What changed

- Added `lai model run` with versioned plan/debug/implement/review/security fixtures in disposable Git repositories.
- Added independent machine validation for exit status, source mutation, expected evidence, and implementation test results.
- Added objective hallucination flags for claimed edits without a diff, claimed passing validation when the independent validator fails, and impossible line references.
- Added isolated per-scenario state/metrics/audit capture for latency, tokens, tool calls, truncation retries, and policy blocks.
- Added model/server/hardware provenance plus executable, fixture, response, and source-state hashes.
- Added `--repeat 1..5`, multi-file scoring, `latest` result resolution, and decision eligibility only after every model-backed scenario has at least two samples.
- Installed the canonical fixture set under `$LAI_DATA_DIR/model-eval` while keeping live result JSONL outside the public repository by default.
- Documented the first local Ministral/Qwen bake-off as preliminary evidence rather than a universal model ranking.

### Safety boundary

- `lai model plan`, `sample`, and `score` remain deterministic and model-free.
- `lai model run` contacts only the already-loaded authenticated endpoint model.
- The runner does not download, start, stop, switch, fine-tune, or select models.
- Fixture repositories are disposable; source checkout HEAD/status must remain invariant.
- Benchmark results cannot automatically replace the default model.

### Why this matters

Model choice and future self-improvement should be driven by observed LAI behavior, not generic benchmark reputation. This cut turns operational successes and failures into repeatable evidence that can later feed regression creation, improvement proposals, and controlled model-selection decisions.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.20 --json
lai model plan --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

## lai harness v0.4.0-beta.19 — release metadata correctness

This beta fixes the release-pack metadata defect discovered while publishing beta.18. Generated GitHub release bodies and annotated-tag messages now come from the exact target-version section in this file instead of stale legacy markers or hardcoded titles.

### What changed

- `release-pack` selects the exact `## lai harness v<TARGET>` section and stops at the next level-2 heading.
- Legacy `### Release body for GitHub` markers in older release sections are ignored.
- Annotated-tag messages are derived from the same target heading as the release body.
- Missing target-specific notes fall back to neutral generic metadata rather than unrelated older release text.
- Current publishing/readiness/checklist documentation is aligned with the actual beta.19 scope.
- Regressions cover stale markers and version-prefix collisions.

### Why this matters

A correct binary can still be published incorrectly if its release evidence describes another version. Release metadata is part of the trust boundary: operators and users should be able to verify that tag, notes, CI evidence, and attached artifact refer to the same cut.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.19 --json
lai release-pack --target 0.4.0-beta.19 --with-vsix --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

## lai harness v0.4.0-beta.18 — versioned runtime records

This beta stabilizes the local state/observability contract before persistent remote sessions. Workspace state, metrics, audit events, and recovery checkpoints now have explicit versioned formats, while retention limits become operator-configurable instead of hidden constants.

### What changed

- Added JSON Schema draft 2020-12 contracts under `schemas/runtime/`.
- New workspace-state, metric, and audit records write `schema_version: 1`; checkpoints share the same version baseline.
- Legacy unversioned records remain readable; unsupported future versions cannot silently become current context/history.
- Added configurable state age, metrics/audit byte thresholds, and retained-tail line counts using normal `CLI > environment > TOML > defaults` precedence.
- JSONL pruning now uses an atomic same-directory replacement.

### Why this matters

Persistent mobile/gateway sessions need durable state formats that can evolve without silently misreading old or newer data. This cut creates that compatibility boundary without adding a database or expanding runtime authority.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.18 --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

# Release notes

## lai harness v0.4.0-beta.17 — Node 24 CI supply-chain hardening

This beta responds to a live GitHub Actions deprecation warning rather than a maturity-score target. CI dependencies move to reviewed Node 24-compatible action releases, immutable SHA pins, and reviewable Dependabot updates.

### What changed

- `actions/checkout` → v7.0.1 at full SHA `3d3c42e5aac5ba805825da76410c181273ba90b1`.
- `actions/setup-python` → v7.0.0 at full SHA `5fda3b95a4ea91299a34e894583c3862153e4b97`.
- `actions/setup-node` → v7.0.0 at full SHA `820762786026740c76f36085b0efc47a31fe5020`.
- Publication packaging now selects Node.js 24 explicitly and disables automatic package-manager caching.
- `.github/dependabot.yml` tracks GitHub Actions weekly so immutable pins can move through normal review.
- A workflow regression sensor rejects floating official-action tags and unreviewed official action dependencies.

### Why this matters

The previous workflow was already being force-run on Node 24 by GitHub while declaring older Node 20 action runtimes. This cut removes that hidden compatibility dependency and makes the external CI toolchain explicit and auditable.

LAI runtime authority, model behavior, remote capability profiles, promotion boundaries, and Python runtime dependencies do not change.

### Validation evidence

- Ruff: green;
- strict mypy: 0 issues on the declared ratchet;
- pytest: 209 passed + 68 subtests;
- unittest publication path: 209 passed;
- publication scan: clean;
- VSIX inspection: passed.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.17 --json
make lint
make typecheck
make check
make test-dev
make test
make harness-score-gate
make validate
```

## lai harness v0.4.0-beta.16 — reproducible quality sensors

This beta hardens the development harness rather than expanding runtime authority. Python quality sensors are now version-locked, strict static type checking is enforced on the first typed guardrail boundary, and CI/publication gates consume the same canonical sensor set.

### What changed

- Added `requirements-dev.in` as the human-maintained development-sensor manifest and generated `requirements.txt` with exact direct/transitive versions.
- Added pinned mypy 2.3.1 with `strict = True` over `.cursor/hooks/feedback_check.py` and `.cursor/hooks/guard_shell.py`.
- Added explicit annotations to those guardrail hooks while preserving fail-closed shell policy and repository-confined feedback behavior.
- Added canonical `make typecheck`; Python 3.11/3.12 CI and the publication gate now enforce it.
- CI installs development sensors from the generated lock; `requirements-dev.txt` remains only a compatibility entrypoint.
- Runtime installation remains standard-library-only and does not install the development lock.
- Removed stale documentation that still described beta.15 workspace promotion as future work.

### Validation evidence

- strict mypy: 2 typed guardrail modules, 0 issues;
- focused quality/hook regressions: 9 tests green before the full run;
- Harness Score 1.6.3: **L4 Self-correcting, 100/108 (93%)**;
- full local gates: **206 tests + 68 pytest subtests**; publication scan clean; VSIX inspection passed.

### Why this matters

A self-correcting harness needs reproducible sensors as much as it needs model/tool guards. This cut makes the quality boundary less dependent on whichever pytest/Ruff/type-checker versions happen to be installed, and establishes a strict type-check ratchet that can expand naturally as `src/local-agent` is split into importable subsystems.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.16 --json
lai release-pack --target 0.4.0-beta.16 --with-vsix --json
make typecheck
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

### Release body for GitHub

lai harness v0.4.0-beta.16 adds reproducible quality sensors: a generated version-pinned development lock, strict mypy enforcement on typed Python guardrail hooks, and CI/publication wiring that makes static type checking a real ratchet rather than a marker file.

Runtime behavior and authority remain unchanged from beta.15: the harness still has no third-party Python runtime dependencies, and MCP/subagent capabilities are intentionally deferred until their governed runtime boundaries exist.

## lai harness v0.4.0-beta.15 — approved workspace promotion

This beta adds the first deterministic approval boundary between an isolated remote work result and a durable Git feature workspace. The model still cannot write the active source checkout or run a remote shell. Promotion acts only on a successful, revalidated, hash-bound patch.

### What changed

- Added `GET /v1/runs/<control_run_id>/promotion` for a read-only promotion proposal.
- Added `POST /v1/runs/<control_run_id>/promotion` accepting exactly one approved `patch_sha256`.
- Source branch, SHA, and clean state are captured by the parent control server before the model starts; mutable safe-workspace metadata is not authoritative.
- Changed-path inventory now uses structured NUL-delimited Git output, fixing the first-filename truncation discovered during real mobile work-run dogfooding.
- Promotion reconstructs a complete binary-capable patch, bounds it, and hashes the exact bytes with SHA-256. The bounded UI diff is evidence only.
- Immediately before Git mutation, the harness repeats the project `full` validation profile in the fixed Docker sandbox and rechecks source SHA/branch/clean state plus patch hash.
- Approved patches are applied to deterministic `lai/promotion-<run-id>` branches in dedicated worktrees under `$LAI_DATA_DIR/promotions`.
- `git apply --check` runs before apply, and the promoted worktree patch must hash to the approved SHA-256 afterwards.
- Repeating the same approved hash is idempotent. Conflicting hashes, source/workspace drift, validation failure, unsafe/oversized patches, failed/cancelled runs, and pre-existing targets fail closed.

### Safety boundary

- Promotion never calls the model.
- Failed or cancelled work runs cannot promote.
- No caller chooses a branch name, destination path, executable, shell command, cwd, environment, Docker options, or validation argv.
- The active source checkout keeps the same HEAD/tree/status; promotion does not switch it or apply files there.
- This cut does not commit, push, open a PR, merge, tag, or publish a release.
- Generic remote `bash` remains absent.

### Validation evidence

Focused control-plane tests now cover source drift, dirty source state, hash mismatch, mutable metadata tampering, route/body/method allowlists, validation failure, exact successful promotion, idempotency, source-checkout invariance, and the path parser regression.

Full local gates reached **200 tests + 68 subtests**. A real Docker + Git smoke in a temporary repository verified:

```text
proposal.promotable = true
validation_exit = 0
branch = lai/promotion-aaaaaaaaaaaaaaaa
hash_match = true
source_head_unchanged = true
source_tree_unchanged = true
source_clean = true
```

### Why this matters

Remote LAI work can now move from a disposable model workspace to a durable reviewable Git workspace without trusting another model turn and without editing the user's active checkout. This creates the correct substrate for the companion gateway to offer explicit **View diff / Promote / Discard** actions. Commit/push/PR remain separate future approvals.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.15 --json
lai release-pack --target 0.4.0-beta.15 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

### Release body for GitHub

lai harness v0.4.0-beta.15 adds approved workspace promotion. Successful isolated work runs can expose an exact SHA-256-bound proposal; approval repeats `full` validation in the existing networkless Docker sandbox, rechecks source and workspace drift, and applies the exact patch to a dedicated `lai/promotion-*` Git worktree/feature branch. The active source checkout remains unchanged.

The endpoint still exposes no generic remote shell, direct active-checkout write, commit, push, merge, dependency installation, or release publication.

## lai harness v0.4.0-beta.14 — isolated remote work runs

Beta.14 introduced isolated remote `implement`, `fix`, `refactor`, and `ci-fix` runs, disposable safe workspaces, structured `validate`, fixed no-network Docker validation, and bounded diff evidence while keeping the source checkout unchanged.

## lai harness v0.4.0-beta.13 — remote capability profiles

Beta.13 added explicit shell-free remote capability profiles and expanded asynchronous control runs to `diagnose` and `release`. Local CLI behavior remained unchanged while control children intersected each mode with a narrower remote tool set before the model received schemas.
