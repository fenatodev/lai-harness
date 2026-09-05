# Release checklist

Use this checklist for beta releases with protected `main`.

## Feature-branch preflight

```bash
cd ~/dev/projects/lai-local-agent
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.21 --json
lai update plan --json
lai release-pack --target 0.4.0-beta.21 --with-vsix --json
make typecheck
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected: version/target aligned, spec 037 complete, update-intelligence regressions green, installation smoke proving the source manifest is available, release metadata aligned with beta.21, and a clean tree after the release commit.

## Update-intelligence review

- Confirm `lai update plan --json` performs no network or model call.
- Confirm `lai update check` refuses to run without explicit `--remote`.
- Confirm remote checks accept only fixed HTTPS metadata hosts, reject redirects/oversized/non-JSON responses, and attach no public-feed credential.
- Confirm PyPI vulnerability evidence is for the exact pinned version.
- Confirm upstream release-note text stays bounded, hashed, and marked untrusted.
- Confirm llama.cpp build/tag scheme mismatches produce manual compatibility review rather than an automatic upgrade recommendation.
- Confirm no `apply`, `install`, `download`, `upgrade`, PR, merge, tag, or publication verb exists in `lai update`.
- Confirm live observations remain under `$LAI_DATA_DIR/update-intelligence`, not the public repository.

## Release metadata review

- Confirm `release-body.md` begins with the exact beta.21 level-2 heading from `docs/RELEASE-NOTES.md`.
- Confirm `human-release-commands.sh` uses the same beta.21 heading for the annotated-tag message.
- Treat neutral generic fallback metadata as a review signal, not preferred release copy.

## Visual documentation review

Every product version bump must review `docs/assets/visual-assets.json`. Regenerate diagrams only if their architecture changed; otherwise update the version marker after explicit review.

## Protected-main integration

1. Push `feature/v0.4.0-beta.21-update-intelligence`.
2. Open a PR into `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the branch up to date.
4. Merge through GitHub without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and verify merged-main CI.

## Tag after merge

Only after `lai release-check --target 0.4.0-beta.21 --json` reports `ready_to_tag`, use the generated `human-release-commands.sh`. Expected annotated message:

```text
v0.4.0-beta.21 — update intelligence
```

Then verify tag CI is green.

## GitHub pre-release

Create the pre-release from `v0.4.0-beta.21`, use the validated pack title/body, attach only the inspected `lai-harness-0.4.0-beta.21.vsix`, and verify remote governance plus the VSIX digest before declaring the cut complete.
