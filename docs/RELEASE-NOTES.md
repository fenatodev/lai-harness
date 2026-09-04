# Release notes

## lai harness v0.4.0-beta.7 — project handoff

This beta keeps the agent behavior stable and adds a portable next-chat handoff flow for long sessions.

### What changed

- Added `lai project-handoff` to render a complete project continuation summary without calling the model.
- Added `lai next-chat` as a concise alias for handoff workflows.
- Added `--out DIR`, `--force`, and `--json` so the handoff can be saved outside the repository.
- Added generated handoff files: `PROJECT-HANDOFF.md`, `NEXT-CHAT-PROMPT.md`, and `summary.json`.
- Added tracked documentation in `docs/PROJECT-HANDOFF.md`.
- Updated beta docs, release checklist, publishing metadata and examples for `0.4.0-beta.7`.

### What stayed intentionally unchanged

- No automatic tag, merge, push, upload, GitHub Release creation, or marketplace publication.
- No model call during project handoff generation.
- No repository file mutation from `lai project-handoff`; generated files live outside the checkout.
- No model redistribution or automatic model download.
- No change to the `lai` CLI command or compatibility IDs.

### Validation gate

Before creating or publishing the release, run:

```bash
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.7 --json
lai release-pack --target 0.4.0-beta.7 --with-vsix --json
lai project-handoff --target 0.4.0-beta.7 --out /tmp/lai-harness-project-handoff-v0.4.0-beta.7 --force --json
make validate
```

After pushing `main` and `v0.4.0-beta.7`, verify that GitHub Actions passes for both refs.

### Release body for GitHub

lai harness v0.4.0-beta.7 is a project-handoff beta. It keeps the stabilized beta line and adds `lai project-handoff`, a deterministic command that renders or writes a portable next-chat handoff containing release posture, branch/tag state, manual GitHub actions, safe workspace state and a ready-to-paste continuation prompt.

The main use case is moving from a long, slow chat to a new one without losing project continuity or asking the model to reconstruct release state from memory. The command remains conservative: it does not tag, merge, push, upload, publish, call the model, run validations, or mutate repository files.

This is not a sandbox and it does not include model weights, llama.cpp, VS Code, or third-party assets.
