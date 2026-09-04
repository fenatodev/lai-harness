# release governance

`lai release-governance` summarizes the local release state and the manual publication actions that remain outside the agent.

```bash
lai release-governance
lai release-governance --json
lai release-governance --target 0.4.0-beta.7 --json
lai governance --json
```

The command is deterministic and read-only. It does not call the model, run validation commands, create tags, merge branches, push, upload assets, publish a GitHub Release, or mutate repository files.

## What it reports

- local `lai release-check` status and phase;
- current branch, HEAD, exact tag and latest reachable tag;
- whether the local release pack files exist in the default `/tmp` location;
- manual action items for GitHub branch protection and GitHub Release publication;
- a machine-readable JSON payload for release operators.

## Why this exists

Beta releases now have deterministic local gates, release packs, protected-branch write guards, and safe workspaces. The remaining risks are mostly operational: forgetting to enable branch protection, forgetting to create the GitHub pre-release, or distributing a VSIX before CI has passed on both `main` and the tag.

`lai release-governance` makes that boundary explicit without pretending the local agent can administer GitHub repository settings.

## Manual GitHub actions

After `main`, tag, local validation and CI are green:

1. Enable branch protection for `main` in GitHub repository settings.
2. Create a GitHub Release from the current tag and mark it as pre-release.
3. Use `release-body.md` from `lai release-pack` as the release body.
4. Attach the inspected VSIX from the release pack only when distributing a manual extension package.


## Chat migration

Use `lai project-handoff --target 0.4.0-beta.7 --out /tmp/lai-harness-project-handoff-v0.4.0-beta.7 --force --json` when a long chat needs to be moved to a fresh session. The generated files are local-only references and should not be published.
