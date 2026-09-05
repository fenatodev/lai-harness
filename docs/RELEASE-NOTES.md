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
