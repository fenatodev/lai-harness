# Release notes

## lai harness v0.4.0-beta.4 — safe workspace dogfood

This beta keeps the agent behavior stable and adds a safer local dogfood workflow for write-capable modes.

### What changed

- Added `lai workspace status` / `lai workspace status --json` to inspect disposable workspaces.
- Added `lai workspace create --name smoke` and `lai workspace clone-smoke` to create standalone copies outside the source checkout.
- Added `lai workspace clean smoke` and `lai workspace clean --all` with path containment checks.
- Safe workspaces initialize their own Git repository on branch `test/lai-smoke`.
- Safe workspace creation copies tracked files only, avoiding untracked files, virtualenvs, runtime state and local secrets.
- Updated beta docs, release checklist, publishing metadata and tests for `0.4.0-beta.4`.

### What stayed intentionally unchanged

- No automatic tag, merge, push, upload, GitHub Release creation, or marketplace publication.
- No automatic execution of `lai implement` inside a safe workspace.
- No model redistribution or automatic model download.
- No bypass of the protected-branch write guard in the source checkout.
- No change to the `lai` CLI command or compatibility IDs.

### Validation gate

Before creating or publishing the release, run:

```bash
lai readiness
lai workspace status --json
lai release-check --target 0.4.0-beta.4 --json
make validate
```

After pushing `main` and `v0.4.0-beta.4`, verify that GitHub Actions passes for both refs.

### Release body for GitHub

lai harness v0.4.0-beta.4 is a safe-workspace dogfood beta. It keeps the stabilized beta line and adds deterministic commands for disposable local workspaces: status, create/clone-smoke and clean.

The main use case is testing write-capable modes such as `implement`, `fix`, and `ci-fix` away from the source checkout. The safe workspace is created outside the repository, seeded from tracked files only, initialized as a standalone Git repo, and placed on `test/lai-smoke` so protected-branch write guards remain intact on `main` and release branches.

This is not a sandbox and it does not include model weights, llama.cpp, VS Code, or third-party assets.
