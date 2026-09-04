# Release notes

## lai harness v0.4.0-beta.9 — self-correcting development harness

This beta closes the repository development feedback loop around lai harness without expanding model autonomy.

### What changed

- Added deterministic `lai policy-check`, which reuses the existing `ALLOW` / `ASK` / `DENY` runtime policy and never executes the requested action.
- Added a repository-local shell gate that delegates to `lai policy-check`, blocks `DENY`, requires review for `ASK`, and fails closed when policy evidence is unavailable.
- Added a repository-confined, best-effort feedback hook for fast syntax/lint feedback after edits.
- Strengthened deterministic denial for force push, hard reset, npm publication, and recursive forced PowerShell deletion.
- Added an explicit `verify-change` workflow for focused-to-full validation.
- Added a separate Harness Score CI workflow pinned to the v1 action revision and gated at L4.
- Extended remote release governance so protected `main` must also require `Harness Score L4`.

### Harness maturity

Harness Score 1.6.3 now measures the repository as **L4 Self-correcting, 93/108 (86%)**, up from beta.8's **L3 Sensing, 76/108 (70%)**. Hooks & Guardrails are 14/14 and CI Feedback remains 14/14.

The remaining score gaps are intentionally not filled with decorative subagent, MCP, type-checker, or lockfile artifacts. They remain candidates only when they solve a concrete project need.

### Safety boundary

- Development hooks are guards, not an OS sandbox.
- The shell hook reuses the same deterministic policy boundary as the product instead of maintaining a divergent denylist.
- Hook failure does not silently become allow.
- Feedback checks are advisory; focused tests and CI remain authoritative.
- The maturity workflow is read-only and separate from product CI.

### Validation gate

```bash
lai readiness
lai policy-check --tool bash --command 'git status --short' --json
lai release-check --target 0.4.0-beta.9 --json
lai release-pack --target 0.4.0-beta.9 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

### Release body for GitHub

lai harness v0.4.0-beta.9 adds a self-correcting repository development harness around the existing local coding agent. The new deterministic `lai policy-check` lets the shell gate reuse the product's `ALLOW` / `ASK` / `DENY` policy without executing commands, while a best-effort feedback hook catches narrow syntax and lint problems immediately after edits.

The repository now gates Harness Score L4 in a separate CI workflow and remote release governance verifies that `Harness Score L4` is required on protected `main`. Harness Score 1.6.3 measures this cut at L4 Self-correcting, 93/108 (86%).
