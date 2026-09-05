# Release notes

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
