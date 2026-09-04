# lai beta readiness

This document records the release posture for `0.4.0-beta.8`. It is a small governance-hardening cut, not an agent architecture expansion.

## Scope

`0.4.0-beta.8` keeps model-assisted behavior stable and adds opt-in remote release verification:

- `lai release-governance --remote` checks GitHub state using GET-only API calls.
- Protected `main` policy is verified for PRs, strict required checks, linear history, administrator enforcement, and disabled force pushes/deletions.
- The expected GitHub pre-release is verified without publication privileges.
- An attached VSIX digest is compared with the local inspected artifact when both digests exist.
- Default governance stays offline/local and model-free.
- Release documentation now follows feature branch -> PR -> CI -> merge -> main CI -> tag -> tag CI -> pre-release.

## Required feature-branch gate

```bash
lai readiness
lai release-check --target 0.4.0-beta.8 --json
lai release-pack --target 0.4.0-beta.8 --with-vsix --json
make lint
make check
make test-dev
make test
make validate
./scripts/install-local.sh
lai version
```

Before merge, `release-check` should report the current version correctly; the tag is intentionally absent. Integration into protected `main` must happen through a PR with all required checks green.

## Post-merge and publication gate

After the PR is merged, update local `main` from `origin/main` and verify main CI. Tag that merged commit as `v0.4.0-beta.8`, push only the tag, verify tag CI, and then create the GitHub pre-release.

Final verification:

```bash
lai release-check --target 0.4.0-beta.8 --json
lai release-governance --target 0.4.0-beta.8 --remote --json
```

Expected final posture: `release-check.phase=released`, remote branch protection `ok`, remote GitHub Release `ok`, and no GitHub governance items left in `manual_actions`.

## Non-goals

The beta cut does not add autonomous GitHub administration, PR creation, merge, tag/push execution, package upload, release publication, model downloading, cron execution, plugin loading, or a stronger shell sandbox.

## Remaining beta risks

- `bash` still runs with the user's OS permissions; the policy gateway is not a sandbox.
- Model-assisted modes remain constrained by the configured local model.
- VS Code Chat Participant API compatibility can vary by VS Code build.
- Signed releases and provenance attestations are not yet implemented.

## Exit criteria

Beta.8 is acceptable when local validation and install smoke pass, protected-main PR/main/tag CI is green, and read-only remote governance verifies the published GitHub state.
