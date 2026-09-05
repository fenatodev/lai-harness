# Release notes

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
