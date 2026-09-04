# Release checklist

Use this checklist for beta releases. It is intentionally manual: lai harness should verify release posture, not tag, merge, push, upload, or publish by itself.

## Local preflight

```bash
cd ~/dev/projects/lai-local-agent
lai readiness
lai release-check --target 0.4.0-beta.3 --json
make check
make validate
./scripts/package-vsix.sh /tmp/lai-harness-0.4.0-beta.3.vsix
```

Expected posture before tagging:

- `lai readiness` reports `Overall: ready`.
- `lai release-check --target 0.4.0-beta.3 --json` reports `phase=ready_to_tag`.
- `make validate` passes.
- VSIX inspection passes.
- Git tree is clean.

## Human release commands

```bash
git tag -a v0.4.0-beta.3   -m "v0.4.0-beta.3 — release polish"

git switch main
git merge --ff-only feature/v0.4.0-beta.3-release-polish

git push --atomic origin main v0.4.0-beta.3
```

## GitHub verification

Verify both refs:

- `main` points to the release commit.
- `v0.4.0-beta.3` is an annotated tag pointing to the same commit.
- GitHub Actions passes for `main`.
- GitHub Actions passes for `v0.4.0-beta.3`.

## Optional GitHub Release

After CI is green:

1. Create a GitHub Release from tag `v0.4.0-beta.3`.
2. Use the title from [GitHub publishing metadata](GITHUB-PUBLISHING.md).
3. Paste the body from [Release notes](RELEASE-NOTES.md).
4. Attach the inspected `/tmp/lai-harness-0.4.0-beta.3.vsix` only if you want to distribute a manual VSIX artifact.
5. Do not mark the release as stable; keep it as beta/pre-release.
