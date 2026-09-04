# Release checklist

Use this checklist for beta releases. It is intentionally manual: lai harness should verify and prepare release posture, not tag, merge, push, upload, or publish by itself.

## Local preflight

```bash
cd ~/dev/projects/lai-local-agent
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.6 --json
lai release-pack --target 0.4.0-beta.6 --with-vsix --json
make check
make validate
```

Expected posture before tagging:

- `lai readiness` reports `Overall: ready`.
- `lai workspace status --json` runs without calling the model.
- `lai release-check --target 0.4.0-beta.6 --json` reports `phase=ready_to_tag`.
- `lai release-pack --target 0.4.0-beta.6 --with-vsix --json` writes files outside the repository.
- `make validate` passes.
- VSIX inspection passes.
- Git tree is clean.

## Human release commands

```bash
git tag -a v0.4.0-beta.6 \
  -m "v0.4.0-beta.6 — release governance"

git switch main
git merge --ff-only feature/v0.4.0-beta.6-release-governance

git push --atomic origin main v0.4.0-beta.6
```

## GitHub verification

Verify both refs:

- `main` points to the release commit.
- `v0.4.0-beta.6` is an annotated tag pointing to the same commit.
- GitHub Actions passes for `main`.
- GitHub Actions passes for `v0.4.0-beta.6`.

## Optional GitHub Release

After CI is green:

1. Create a GitHub Release from tag `v0.4.0-beta.6`.
2. Use the title from [GitHub publishing metadata](GITHUB-PUBLISHING.md).
3. Paste `release-body.md` from the release pack, or copy the body from [Release notes](RELEASE-NOTES.md).
4. Attach the inspected `lai-harness-0.4.0-beta.6.vsix` from the release pack only if you want to distribute a manual VSIX artifact.
5. Do not mark the release as stable; keep it as beta/pre-release.
