# Release checklist

Use this checklist for beta releases with protected `main`.

## Feature-branch preflight

```bash
cd ~/dev/projects/lai-local-agent
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.24 --json
lai semantics --json
lai release-pack --target 0.4.0-beta.24 --with-vsix --json
make typecheck
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

Expected: version/target aligned, spec 040 complete, semantic source/install regressions green, strict mypy includes the extracted module, release metadata aligned with beta.24, and a clean tree after the release commit.

## Modularization review

- Confirm `src/lai_semantics.py` is standard-library-only and passes strict mypy.
- Confirm `src/local-agent` imports/re-exports the semantic behavior rather than retaining a second contract copy.
- Confirm `lai semantics` and `lai semantic --json` remain deterministic without a model server.
- Confirm semantic context ranking still emits `semantic_contract:<subsystem>` reasons.
- Confirm the contract advertises `src/lai_semantics.py` as canonical for `semantic-code-contracts`.
- Confirm an isolated `install-local.sh` copy contains `lai_semantics.py` and installed `lai semantics` works.
- Confirm no policy, network, model, control-plane, Git, or update authority changed in this cut.

## Release metadata review

- Confirm `release-body.md` begins with the exact beta.24 level-2 heading from `docs/RELEASE-NOTES.md`.
- Confirm `human-release-commands.sh` uses the same beta.24 heading for the annotated-tag message.
- Treat neutral generic fallback metadata as a review signal, not preferred release copy.

## Visual documentation review

Every product version bump must review `docs/assets/visual-assets.json`. Beta.24 changes source-module boundaries but not the external four-layer architecture or protected release flow, so existing diagrams may keep their images if explicitly reviewed and the version marker is advanced.

## Protected-main integration

1. Push `feature/v0.4.0-beta.24-semantic-contract-modularization`.
2. Open a PR into `main`.
3. Require `Python 3.11`, `Python 3.12`, `Publication gates`, and `Harness Score L4` with the branch up to date.
4. Merge through GitHub without bypassing branch protection.
5. Fast-forward local `main` to `origin/main` and verify merged-main CI.

## Tag after merge

Only after `lai release-check --target 0.4.0-beta.24 --json` reports `ready_to_tag`, use the generated `human-release-commands.sh`. Expected annotated message:

```text
v0.4.0-beta.24 — semantic contract modularization
```

Then verify tag CI is green.

## GitHub pre-release

Create the pre-release from `v0.4.0-beta.24`, use the validated pack title/body, attach only the inspected `lai-harness-0.4.0-beta.24.vsix`, and verify remote governance plus the VSIX digest before declaring the cut complete.
