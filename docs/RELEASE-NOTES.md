# Release notes

## lai harness v0.4.0-beta.3 — release polish

This beta keeps the agent behavior stable and focuses on making the project easier to publish, inspect, and evaluate from the outside.

### What changed

- Updated public release metadata for the current `fenatodev/lai-harness` repository.
- Added ready-to-paste GitHub Release notes for the beta line.
- Added a human release checklist that separates local validation, tag creation, GitHub CI verification, and optional VSIX attachment.
- Updated quick-start and release-check examples to target `0.4.0-beta.3`.
- Renamed generated VSIX artifact defaults from `lai-local-agent-*` to `lai-harness-*` while preserving compatibility identifiers where they are part of the extension contract.

### What stayed intentionally unchanged

- No automatic tag, merge, push, upload, or marketplace publication.
- No model redistribution or automatic model download.
- No expansion of autonomous powers, background execution, cron, plugin execution, or sandbox claims.
- No change to the `lai` CLI command or compatibility IDs.

### Validation gate

Before creating or publishing the release, run:

```bash
lai readiness
lai release-check --target 0.4.0-beta.3 --json
make validate
```

After pushing `main` and `v0.4.0-beta.3`, verify that GitHub Actions passes for both refs.

### Release body for GitHub

lai harness v0.4.0-beta.3 is a release-polish beta. It keeps the stabilized beta.1 agent behavior and improves the public release surface: current GitHub publishing metadata, ready-to-paste release notes, a manual release checklist, beta-targeted quick-start examples, and public `lai-harness-*` VSIX artifact naming.

The harness remains local-first and experimental. It is designed for constrained local LLMs through compact mode-specific tools, repository-confined file operations, validation/evidence guards, run history, sanitized run export, readiness checks, and deterministic release preflight.

This is not a sandbox and it does not include model weights, llama.cpp, VS Code, or third-party assets.
