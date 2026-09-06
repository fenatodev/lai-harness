# release governance

`lai release-governance` summarizes local release posture. `--remote` additionally verifies GitHub state through read-only API requests.

![LAI protected release flow](assets/release-flow.png)

```bash
lai release-governance --target 0.4.1 --json
lai release-governance --target 0.4.1 --remote --json
lai governance --remote --json
```

Without `--remote`, the command is deterministic, model-free, and repository-read-only. With `--remote`, it performs GitHub API GET requests only; it never changes repository settings or publishes anything.

## Remote verification

The remote check resolves `owner/repo` from Git `origin` and verifies:

- `main` requires pull requests;
- required checks are strict/up-to-date and include `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4`;
- linear history and administrator enforcement are enabled;
- force pushes and branch deletion are disabled;
- the expected GitHub Release exists, is published (`draft=false`), and its `prerelease` flag matches the target channel;
- when both sides expose the VSIX digest, published SHA-256 matches the local inspected VSIX.

A prerelease target requires `prerelease=true`; a stable target such as `0.4.0` requires `prerelease=false`. A channel mismatch remains actionable even when the tag is otherwise correct.

Credentials are read in this order: `GH_TOKEN`, `GITHUB_TOKEN`, then non-interactive `git credential fill`. Credentials are never included in governance output. Missing credentials or unavailable APIs remain `unverified` rather than being guessed.

## Manual actions

Offline governance keeps GitHub actions explicit. The generated release action tells the operator whether the pre-release flag must be enabled or disabled for the target. Under `--remote`, verified actions disappear from `manual_actions`; missing, incomplete, or unverified state remains actionable. An attached VSIX with a digest mismatch blocks governance.

## Protected-main release flow

Never push release commits directly to protected `main`. Use the reviewed branch/PR flow in [Release checklist](RELEASE-CHECKLIST.md), tag the resulting synchronized `main` commit only after green post-merge CI, and publish only after tag CI succeeds.

## Chat migration

`lai project-handoff --target <target-version> --remote --json` can carry the same live release-governance evidence into another session. Omit `--remote` for a fully offline handoff.
