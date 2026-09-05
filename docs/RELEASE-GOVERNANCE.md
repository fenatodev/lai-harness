# release governance

`lai release-governance` summarizes local release posture. `--remote` additionally verifies the GitHub state with read-only API requests.

![LAI protected release flow](assets/release-flow.png)

```bash
lai release-governance
lai release-governance --json
lai release-governance --target 0.4.0-beta.21 --remote --json
lai governance --remote --json
```

Without `--remote`, the command remains deterministic, offline, model-free, and repository-read-only. With `--remote`, it performs GitHub API GET requests only; it never changes repository settings or publishes anything.

## Remote verification

The remote check resolves `owner/repo` from the Git `origin` and verifies:

- `main` requires pull requests;
- required status checks are strict/up-to-date and include `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`;
- linear history and administrator enforcement are enabled;
- force pushes and branch deletion are disabled;
- the expected GitHub Release exists, is published, and is marked as a pre-release;
- when both sides expose the VSIX digest, the published artifact SHA-256 matches the local inspected VSIX.

Credentials are read in this order: `GH_TOKEN`, `GITHUB_TOKEN`, then non-interactive `git credential fill`. Credentials are never included in governance output. A missing credential or unavailable API leaves the relevant action `unverified` instead of guessing.

## Manual actions

Default/offline governance keeps GitHub actions explicit. Under `--remote`, a verified action disappears from `manual_actions`; missing, incomplete, or unverified state remains actionable. A VSIX upload remains optional, but an attached VSIX with a digest mismatch blocks governance.

## Protected-main release flow

Once `main` is protected, do not push release commits directly to it. Use the feature branch and PR flow in [Release checklist](RELEASE-CHECKLIST.md), then tag the resulting `main` commit only after merge and green CI.

## Chat migration

Use `lai project-handoff --target 0.4.0-beta.21 --remote --out /tmp/lai-harness-project-handoff-v0.4.0-beta.21 --force --json` when a long chat needs live GitHub release evidence in the next session. Omit `--remote` for a fully offline handoff.
