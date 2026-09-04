# Release notes

## lai harness v0.4.0-beta.6 — release governance

This beta keeps the agent behavior stable and improves the manual publication workflow.

### What changed

- Added `lai release-governance` to summarize local release posture and remaining manual GitHub publication actions.
- Added `lai governance` as a concise alias and `--json` for automation-friendly metadata.
- Added release-governance checks for branch protection and GitHub pre-release publication as explicit manual actions.
- Added overwrite protection with `--force` and repository-write refusal for release pack output paths.
- Added release pack documentation and tests.
- Updated beta docs, release checklist, publishing metadata and examples for `0.4.0-beta.6`.

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
lai release-check --target 0.4.0-beta.6 --json
lai release-pack --target 0.4.0-beta.6 --with-vsix --json
make validate
```

After pushing `main` and `v0.4.0-beta.6`, verify that GitHub Actions passes for both refs.

### Release body for GitHub

lai harness v0.4.0-beta.6 is a release-governance beta. It keeps the stabilized beta line and adds `lai release-governance`, a deterministic read-only command that summarizes local release state, release-pack presence, and remaining manual GitHub publication actions.

The main use case is publishing a GitHub pre-release without asking the model to invent release steps or manually copy scattered documentation. The command remains conservative: it does not tag, merge, push, upload, publish, call the model, or mutate repository files.

This is not a sandbox and it does not include model weights, llama.cpp, VS Code, or third-party assets.
