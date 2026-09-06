# Release checklist

Use this checklist for both pre-release and stable targets with protected `main`. Substitute the intended target version in the commands below; `release-check` and `release-pack` are authoritative for the expected tag and release channel.

## Feature-branch preflight

```bash
lai readiness
lai workspace status --json
lai release-check --target <target-version> --json
lai semantics --json
lai release-pack --target <target-version> --with-vsix --json
make milestone-gate
```

Expected: version/target aligned, no invalid active spec, a clean tree after the release commit, full local gates green, and release-pack evidence that reports `release_channel` plus `expected_prerelease`.

For the first stable `0.4.0` release, also satisfy [Stable readiness](STABLE-READINESS.md) before the public version bump is integrated.

## Release metadata review

- Confirm `release-body.md` comes from the exact target section in `docs/RELEASE-NOTES.md`; neutral fallback copy is a review signal, not preferred release copy.
- Confirm `human-release-commands.sh` uses the exact expected tag and reviewed title.
- Confirm the VSIX filename/version equals the target version.
- Confirm `expected_prerelease=true` for SemVer prerelease targets and `false` for a stable target such as `0.4.0`.

## Visual documentation review

Every product version bump must review `docs/assets/visual-assets.json`. Regenerate diagrams only when the architecture they describe changed; otherwise explicitly advance the version marker after review.

## Protected-main integration

1. Push the reviewed feature/stabilization branch.
2. Open a PR into `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the branch up to date.
4. Merge without bypassing branch protection or linear-history rules.
5. Fast-forward local `main` to `origin/main` and verify merged-main CI.

## Tag after merge

Only after `lai release-check --target <target-version> --json` reports `ready_to_tag`, create the annotated expected tag from synchronized `main` and push only that tag. Then require tag CI and publication gates to be green.

## GitHub Release

Create the release from the exact expected tag, use the validated pack title/body, and attach only the inspected VSIX. For a prerelease target, enable GitHub's pre-release flag. For a stable target, leave that flag disabled. Finally run remote release governance and verify the VSIX digest before declaring the cut complete.
