# Release checklist

Use this checklist for beta releases with protected `main`.

## Feature-branch preflight

```bash
cd ~/dev/projects/lai-local-agent
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.11 --json
lai release-pack --target 0.4.0-beta.11 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected: version/target aligned, validation and VSIX inspection green, Harness Score L4 satisfied, and a clean tree after the release commit.

## Protected-main integration

1. Push `feature/v0.4.0-beta.11-local-control-plane`.
2. Open a PR into `main`.
3. Confirm all required checks are present; `Harness Score L4` is already part of protected `main`.
4. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the branch up to date.
5. Merge through GitHub; do not bypass branch protection or push the release commit directly to `main`.
6. Fast-forward local `main` to `origin/main` and verify GitHub Actions on the merged commit.

## Tag after merge

Only after merged `main` is green and `lai release-check --target 0.4.0-beta.11 --json` reports `ready_to_tag`:

```bash
git tag -a v0.4.0-beta.11 \
  -m "v0.4.0-beta.11 — local control plane foundation"
git push origin v0.4.0-beta.11
```

Then verify tag CI is green.

## GitHub pre-release

1. Create the GitHub Release from `v0.4.0-beta.11`.
2. Use the title/body from the release pack.
3. Keep it marked as pre-release.
4. Optionally attach the inspected `lai-harness-0.4.0-beta.11.vsix`.
5. Run `lai release-governance --target 0.4.0-beta.11 --remote --json` and `lai project-handoff --target 0.4.0-beta.11 --remote --json`; published governance should be fully verified.
