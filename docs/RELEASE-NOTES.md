# Release notes

## lai harness v0.4.0-beta.8 — remote release governance

This beta closes the gap between local release posture and the public GitHub state without making release-governance a write-capable command.

### What changed

- Added `lai release-governance --remote` for opt-in GitHub verification.
- Verifies protected `main` policy: PRs, strict required checks, linear history, admin enforcement, and disabled force pushes/deletions.
- Verifies the expected GitHub Release is a published pre-release.
- Compares the local inspected VSIX SHA-256 with the GitHub asset digest when both are available.
- Verified GitHub items are removed from `manual_actions`; missing/unverified state stays actionable.
- Updated release documentation to use the protected-main PR workflow before tagging.

### Safety boundary

- Default `lai release-governance` remains offline/local.
- `--remote` performs GitHub API GET requests only.
- No GitHub settings mutation, PR creation, merge, tag, push, upload, or Release publication.
- No model call and no repository mutation from governance verification.
- Credentials are consumed without being rendered in output.

### Validation gate

```bash
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.8 --json
lai release-pack --target 0.4.0-beta.8 --with-vsix --json
lai release-governance --target 0.4.0-beta.8 --remote --json
lai project-handoff --target 0.4.0-beta.8 --out /tmp/lai-harness-project-handoff-v0.4.0-beta.8 --force --json
make check
make validate
```

### Release body for GitHub

lai harness v0.4.0-beta.8 adds opt-in remote release governance. `lai release-governance --remote` can now verify the protected `main` policy and the published GitHub pre-release without changing GitHub state.

When an inspected local VSIX and GitHub asset digest are both available, the command compares SHA-256 so the public artifact can be tied back to the local release pack. The default governance command remains offline, and all remote behavior is GET-only and model-free.

This beta also updates the release flow for protected `main`: release work goes through a feature branch and PR, then the merged `main` commit is tagged after green CI.
