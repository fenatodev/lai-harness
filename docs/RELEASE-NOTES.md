# Release notes

## lai harness v0.4.0-beta.5 — release publication pack

This beta keeps the agent behavior stable and improves the manual publication workflow.

### What changed

- Added `lai release-pack` to generate a local publication pack outside the source repository.
- Added `lai release-pack --json` for automation-friendly metadata.
- Added `lai release-pack --with-vsix` to put the inspected VSIX beside the release notes and checklist.
- Added overwrite protection with `--force` and repository-write refusal for release pack output paths.
- Added release pack documentation and tests.
- Updated beta docs, release checklist, publishing metadata and examples for `0.4.0-beta.5`.

### What stayed intentionally unchanged

- No automatic tag, merge, push, upload, GitHub Release creation, or marketplace publication.
- No model call during release pack generation.
- No repository file mutation from `lai release-pack`; generated files live outside the checkout.
- No model redistribution or automatic model download.
- No change to the `lai` CLI command or compatibility IDs.

### Validation gate

Before creating or publishing the release, run:

```bash
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.5 --json
lai release-pack --target 0.4.0-beta.5 --with-vsix --json
make validate
```

After pushing `main` and `v0.4.0-beta.5`, verify that GitHub Actions passes for both refs.

### Release body for GitHub

lai harness v0.4.0-beta.5 is a release-publication beta. It keeps the stabilized beta line and adds `lai release-pack`, a deterministic local command that prepares release body, checklist, publishing metadata, human-run commands, summary JSON and optional VSIX output outside the source checkout.

The main use case is publishing a GitHub pre-release without asking the model to invent release steps or manually copy scattered documentation. The command remains conservative: it does not tag, merge, push, upload, publish, call the model, or mutate repository files.

This is not a sandbox and it does not include model weights, llama.cpp, VS Code, or third-party assets.
