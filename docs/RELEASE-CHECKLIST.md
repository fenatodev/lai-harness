# Release checklist

Use this checklist for beta releases with protected `main`.

## Feature-branch preflight

```bash
cd ~/dev/projects/lai-local-agent
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.19 --json
lai release-pack --target 0.4.0-beta.19 --with-vsix --json
make typecheck
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected: version/target aligned, generated release title/body aligned with beta.19, validation and VSIX inspection green, Harness Score L4 satisfied, and a clean tree after the release commit.

## Release metadata review

- Confirm `release-body.md` begins with the exact beta.19 level-2 heading from `docs/RELEASE-NOTES.md`.
- Confirm it contains no content from older release sections.
- Confirm `human-release-commands.sh` uses the same beta.19 heading for the annotated-tag message.
- Treat the neutral generic fallback as a review signal, not as preferred release copy.

## Visual documentation review

Every product version bump must review `docs/assets/visual-assets.json`. Regenerate diagrams only if their architecture changed; otherwise update the version marker after explicit review.

## Protected-main integration

1. Push `feature/v0.4.0-beta.19-release-notes-correctness`.
2. Open a PR into `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the branch up to date.
4. Merge through GitHub without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and verify merged-main CI.

## Tag after merge

Only after `lai release-check --target 0.4.0-beta.19 --json` reports `ready_to_tag`, use the generated `human-release-commands.sh`. The expected annotated message is:

```text
v0.4.0-beta.19 — release metadata correctness
```

Then verify tag CI is green.

## GitHub pre-release

1. Create the Release from `v0.4.0-beta.19`.
2. Use title/body from the validated release pack.
3. Keep it marked as pre-release.
4. Attach only the inspected `lai-harness-0.4.0-beta.19.vsix` when publishing the extension artifact.
5. Verify remote governance and the VSIX digest before declaring the cut complete.