# Release checklist

Use this checklist for beta releases with protected `main`.

## Feature-branch preflight

```bash
cd ~/dev/projects/lai-local-agent
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.20 --json
lai model plan --json
lai release-pack --target 0.4.0-beta.20 --with-vsix --json
make typecheck
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected: version/target aligned, spec 036 complete, automated model-evaluation regressions green, generated release title/body aligned with beta.20, validation/VSIX inspection green, and a clean tree after the release commit.

## Model-evaluation review

- Confirm `lai model plan --json` remains deterministic and does not contact the model endpoint.
- Confirm `lai model run` uses only the already-loaded authenticated model and disposable fixture repositories.
- Confirm live benchmark results are written under `$LAI_DATA_DIR/model-eval`, not committed to the public repository.
- Confirm no benchmark run changes the configured default model, starts/stops a model server, or mutates the source checkout.
## Release metadata review

- Confirm `release-body.md` begins with the exact beta.20 level-2 heading from `docs/RELEASE-NOTES.md`.
- Confirm `human-release-commands.sh` uses the same beta.20 heading for the annotated-tag message.
- Treat neutral generic fallback metadata as a review signal, not preferred release copy.

## Visual documentation review

Every product version bump must review `docs/assets/visual-assets.json`. Regenerate diagrams only if their architecture changed; otherwise update the version marker after explicit review.

## Protected-main integration

1. Push `feature/v0.4.0-beta.20-automated-model-evaluation`.
2. Open a PR into `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the branch up to date.
4. Merge through GitHub without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and verify merged-main CI.

## Tag after merge

Only after `lai release-check --target 0.4.0-beta.20 --json` reports `ready_to_tag`, use the generated `human-release-commands.sh`. Expected annotated message:

```text
v0.4.0-beta.20 — automated model evaluation
```
Then verify tag CI is green.

## GitHub pre-release

1. Create the Release from `v0.4.0-beta.20`.
2. Use title/body from the validated release pack.
3. Keep it marked as pre-release.
4. Attach only the inspected `lai-harness-0.4.0-beta.20.vsix`.
5. Verify remote governance and the VSIX digest before declaring the cut complete.
