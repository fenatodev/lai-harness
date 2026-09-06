# release pack

`lai release-pack` writes a local publication pack for either a pre-release or a stable release target.

It prepares evidence for a human-controlled GitHub Release. It does not create tags, merge branches, push commits, upload assets, publish a release, call the model, or mutate repository files.

## Commands

```bash
lai release-pack --target 0.4.0-beta.24 --json
lai release-pack --target 0.4.0 --json
lai release-pack --target <target-version> --with-vsix
lai release-pack --target <target-version> --out /tmp/lai-harness-release-pack-<target-version>
```

By default the pack is written under `/tmp/lai-harness-release-pack-v<target-version>`.

## Files

A release pack contains:

- `summary.json` — release-check status, channel, expected GitHub prerelease state, target tag, branch, HEAD, and generated file paths;
- `release-body.md` — target-specific GitHub Release body from `docs/RELEASE-NOTES.md` or a channel-correct neutral fallback;
- `release-checklist.md` — copied channel-neutral human checklist;
- `github-publishing.md` — copied public publishing guidance;
- `human-release-commands.sh` — documentation-only Git/tag commands;
- `lai-harness-<target-version>.vsix` — only when `--with-vsix` is used.

## Channel behavior

SemVer targets with a prerelease suffix (for example `-alpha`, `-beta`, or `-rc`) report `release_channel=prerelease` and `expected_prerelease=true`. A plain target such as `0.4.0` reports `release_channel=stable` and `expected_prerelease=false`. Channel is derived from the target version, never from release-note prose.

## Safety behavior

- Refuses to write the pack inside the source repository.
- Refuses to overwrite a non-empty output directory unless `--force` is passed.
- Uses deterministic `release-check` evidence.
- Does not bypass protected-branch guards.
- Does not require the local model server for pack generation itself.

## Suggested flow

Run readiness and the full local validation gate on the release branch, integrate through protected `main`, verify merged-main CI, create only the expected annotated tag, wait for tag CI, then publish the frozen pack. Enable GitHub's pre-release flag only when the pack reports `expected_prerelease=true`.
