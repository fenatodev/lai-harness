# lai beta readiness

This document records the release posture for `0.4.0-beta.9`. It is a development-harness hardening cut: model-assisted product behavior stays stable while deterministic repository feedback closes the Harness Score L4 loop.

## Scope

`0.4.0-beta.9` adds:

- deterministic, model-free `lai policy-check` with `executed: false` evidence;
- a policy-backed `beforeShellExecution` gate that maps `ALLOW` / `ASK` / `DENY` and fails closed;
- a repository-confined, best-effort `afterFileEdit` feedback hook;
- stronger `DENY` coverage for force push, hard reset, npm publication, and recursive forced PowerShell deletion;
- an explicit `verify-change` workflow;
- a dedicated Harness Score workflow gated at L4;
- remote release governance that also requires `Harness Score L4` on protected `main`.

The measured repository maturity is L4 Self-correcting, 93/108 (86%), using Harness Score 1.6.3.

## Required feature-branch gate

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
./scripts/install-local.sh
lai version
```

Before merge, the beta.9 tag and GitHub Release are intentionally absent. The PR must run both product CI and `Harness Score L4` successfully.

## Protected-main integration

After the first beta.9 PR exposes the new check, add `Harness Score L4` to the required status checks for `main`. Do not merge until all four required checks are green and the branch is up to date.

After merge, sync local `main`, verify main CI, tag the merged commit as `v0.4.0-beta.9`, push only the tag, verify tag CI, and then create the GitHub pre-release.

Final verification:

```bash
lai release-check --target 0.4.0-beta.9 --json
lai release-governance --target 0.4.0-beta.9 --remote --json
```

Expected final posture: `release-check.phase=released`, remote branch protection `ok`, GitHub Release `ok`, VSIX digest matching when attached, and no remaining `manual_actions`.

## Non-goals

This cut does not add autonomous GitHub administration, a fake subagent, MCP merely for scoring, a type checker without a typing plan, automatic dependency installation, model downloading, or a stronger OS sandbox.

## Remaining beta risks

- Allowed `bash` still executes with the user's OS permissions; hooks and policy are guards, not containment.
- Model-assisted modes remain constrained by the configured local model.
- VS Code/Cursor integration behavior can vary by host version; CI remains authoritative.
- Signed releases and provenance attestations are not yet implemented.
