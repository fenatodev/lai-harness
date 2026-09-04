# Release checklist

Use this checklist for beta releases after `main` branch protection is enabled.

## Feature-branch preflight

```bash
cd ~/dev/projects/lai-local-agent
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.8 --json
lai release-pack --target 0.4.0-beta.8 --with-vsix --json
make check
make validate
```

Expected: current version matches the target, validation passes, VSIX inspection passes, and the Git tree is clean after the release commit.

## Protected-main integration

1. Push `feature/v0.4.0-beta.8-remote-governance`.
2. Open a PR into `main`.
3. Require `Python 3.11`, `Python 3.12`, and `Publication gates` to pass with the branch up to date.
4. Merge through GitHub; do not bypass branch protection or push the release commit directly to `main`.
5. Fetch/switch to `main` locally and fast-forward to `origin/main`.
6. Verify GitHub Actions on the resulting `main` commit.

## Tag after merge

Only after merged `main` is green:

```bash
git tag -a v0.4.0-beta.8 \
  -m "v0.4.0-beta.8 — remote release governance"
git push origin v0.4.0-beta.8
```

Then verify tag CI is green.

## GitHub pre-release

1. Create the GitHub Release from `v0.4.0-beta.8`.
2. Use the title/body from the release pack.
3. Keep it marked as pre-release.
4. Optionally attach the inspected `lai-harness-0.4.0-beta.8.vsix`.
5. Run `lai release-governance --target 0.4.0-beta.8 --remote --json`; published governance should be fully verified.
