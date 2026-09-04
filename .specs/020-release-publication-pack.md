# 020 release publication pack

## Status

Implemented for `0.4.0-beta.5`.

## Problem

Publishing a beta requires copying release notes, checklist details, commands and optionally a VSIX from several places. That manual assembly invites stale version numbers or accidental publication steps.

## Requirements

- R1: Provide a deterministic `lai release-pack` command.
- R2: Write generated release files outside the source repository by default.
- R3: Refuse output paths inside the repository.
- R4: Generate `release-body.md`, `release-checklist.md`, `github-publishing.md`, `human-release-commands.sh` and `summary.json`.
- R5: Support `--with-vsix` for optional local VSIX packaging.
- R6: Support `--json`, `--target`, `--out` and `--force`.
- R7: Do not tag, merge, push, upload, publish, call the model, or mutate repository files.

## Validation

- `make check`
- Focused release-pack unit and install-smoke tests
- Full `pytest` / `unittest`
- `make validate`
- Installed smoke: `lai release-pack --target 0.4.0-beta.5 --out /tmp/... --with-vsix --json`

## Traceability

- R1 -> `render_release_pack`, `parse_release_pack_args`
- R2 -> `release_pack_default_dir`
- R3 -> `release_pack_resolve_out_dir`
- R4 -> `write_release_pack`, `release_pack_files`
- R5 -> `write_release_pack` VSIX branch
- R6 -> parser tests
- R7 -> release-pack safety tests and release-check policy
