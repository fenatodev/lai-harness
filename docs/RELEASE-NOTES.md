# Release notes

## lai harness v0.4.0-beta.10 — release state convergence

This beta makes release state harder to misread and harder to tag from the wrong commit.

### What changed

- Added opt-in `lai project-handoff --remote` and `lai next-chat --remote`.
- Handoff output now preserves the local/offline governance result while also exposing the remote governance result when requested.
- The effective handoff status and `manual_actions` come from remote verification when `--remote` is enabled.
- Remote handoff evidence includes protected-main status, GitHub pre-release state, credential source metadata, and VSIX digest comparison without rendering credentials.
- `lai release-check` now resolves the expected tag target directly and blocks if the tag already points to another commit.
- A clean feature branch reports `ready_for_integration`; it can no longer report `ready_to_tag`.
- `ready_to_tag` requires `main`, a clean/readiness-valid checkout, and `HEAD == origin/main`.
- A tag is considered `released` only when it peels to synchronized `main` HEAD.

### Why this matters

Beta.9 could verify a published release remotely, but `project-handoff` still recorded only offline governance and therefore reported `action_required` after publication. Separately, the beta.8 release exposed a tag-target hazard: a release tag could exist on an older commit before the intended protected-main integration was complete.

Beta.10 converts both incidents into deterministic checks instead of relying on operator memory.

### Harness maturity

Harness Score remains **L4 Self-correcting, 93/108 (86%)**. This beta does not add decorative score artifacts; it improves release correctness using mechanisms the project already needs.

### Safety boundary

- Default `release-check`, `release-governance`, and `project-handoff` remain model-free and repository-read-only.
- `project-handoff --remote` reuses the existing GitHub GET-only governance path.
- No remote handoff path can tag, merge, push, upload, publish, or change branch protection.
- Offline tag readiness uses only local Git metadata and the local `origin/main` tracking ref; GitHub CI remains an explicit separate gate.

### Validation gate

```bash
lai readiness
lai release-check --target 0.4.0-beta.10 --json
lai release-pack --target 0.4.0-beta.10 --with-vsix --json
lai project-handoff --target 0.4.0-beta.10 --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

### Release body for GitHub

lai harness v0.4.0-beta.10 converges release state across `release-check`, remote governance, and project handoff. Feature branches now report `ready_for_integration`; `ready_to_tag` is reserved for synchronized protected `main`, and an expected tag pointing at another commit blocks the release check.

The handoff can optionally include live GitHub verification with `--remote`, preserving local/offline evidence while using verified branch protection, pre-release state, and VSIX digest evidence as the effective release posture. Remote verification remains GET-only and model-free. Harness Score remains L4 Self-correcting at 93/108 (86%).
