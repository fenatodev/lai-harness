# Release checklist

Use this checklist for beta releases with protected `main`.

## Feature-branch preflight

```bash
cd ~/dev/projects/lai-local-agent
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.15 --json
lai release-pack --target 0.4.0-beta.15 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected: version/target aligned, validation and VSIX inspection green, Harness Score L4 satisfied, and a clean tree after the release commit.

## Visual documentation review

Every product version bump must review `docs/assets/visual-assets.json`. Its `reviewed_for_version` must equal the runtime version or CI fails.

- If core architecture, mobile/control boundaries, or release flow changed, regenerate the affected diagrams and review their labels against current code/docs.
- If architecture did not change, update the marker only after explicitly confirming the existing diagrams remain accurate.
- Treat diagrams as explanatory artifacts; security claims must still be supported by tests and `docs/SECURITY-MODEL.md`.

## Protected-main integration

1. Push `feature/remote-work-profile`.
2. Open a PR into `main`.
3. Confirm all required checks are present; `Harness Score L4` is already part of protected `main`.
4. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the branch up to date.
5. Merge through GitHub; do not bypass branch protection or push the release commit directly to `main`.
6. Fast-forward local `main` to `origin/main` and verify GitHub Actions on the merged commit.

## Tag after merge

Only after merged `main` is green and `lai release-check --target 0.4.0-beta.15 --json` reports `ready_to_tag`:

```bash
git tag -a v0.4.0-beta.15 \
  -m "v0.4.0-beta.15 — approved workspace promotion"
git push origin v0.4.0-beta.15
```

Then verify tag CI is green.

## GitHub pre-release

1. Create the GitHub Release from `v0.4.0-beta.15`.
2. Use the title/body from the release pack.
3. Keep it marked as pre-release.
4. Optionally attach the inspected `lai-harness-0.4.0-beta.15.vsix`.
5. Run `lai release-governance --target 0.4.0-beta.15 --remote --json` and `lai project-handoff --target 0.4.0-beta.15 --remote --json`; published governance should be fully verified.
