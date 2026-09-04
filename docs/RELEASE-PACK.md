# release pack

`lai release-pack` writes a local publication pack for a beta release.

It is for preparing a GitHub Release by hand. It does not create tags, merge branches, push commits, upload assets, publish a GitHub Release, call the model, or mutate repository files.

## Commands

```bash
lai release-pack --target 0.4.0-beta.7
lai release-pack --target 0.4.0-beta.7 --json
lai release-pack --target 0.4.0-beta.7 --with-vsix
lai release-pack --target 0.4.0-beta.7 --out /tmp/lai-harness-release-pack-v0.4.0-beta.7
```

By default the pack is written outside the repository under:

```text
/tmp/lai-harness-release-pack-v0.4.0-beta.7
```

## Files

A release pack contains:

- `summary.json` — release-check status, target tag, branch, HEAD and generated file paths.
- `release-body.md` — ready-to-paste GitHub Release body from `docs/RELEASE-NOTES.md`.
- `release-checklist.md` — copied human release checklist.
- `github-publishing.md` — copied public publishing metadata.
- `human-release-commands.sh` — documentation-only commands for the human operator.
- `lai-harness-0.4.0-beta.7.vsix` — only when `--with-vsix` is used.

## Safety behavior

- Refuses to write the pack inside the source repository.
- Refuses to overwrite a non-empty output directory unless `--force` is passed.
- Uses `lai release-check` data for phase and readiness posture.
- Does not bypass protected-branch write guards.
- Does not require the local model server.

## Suggested flow

```bash
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.7 --json
lai release-pack --target 0.4.0-beta.7 --with-vsix --json
make validate
```

After the human-created tag and push, verify GitHub Actions for both `main` and `v0.4.0-beta.7` before creating the GitHub Release as a pre-release.
