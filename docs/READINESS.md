# readiness

`lai readiness` checks whether the current repository and local environment are ready for a safe lai harness work session.

```bash
lai readiness
lai readiness --json
lai ready
```

The command reads local configuration, Git state, skill installation, recovery status, run history, and authenticated server health. It does not call the model, start the server, replay prior tool calls, execute release commands, or mutate repository files.

## output

The human output includes an overall status:

- `ready`: required checks passed.
- `attention`: non-blocking warnings exist, such as a dirty Git tree or no recorded runs.
- `blocked`: an operational prerequisite is missing, such as unavailable Git evidence, missing mode skills, failed server authentication, invalid active spec, or recovery inspection failure.

JSON output exposes the same checks for scripts and future VS Code integration. API key contents are never printed.


After readiness is healthy, use `lai run export --last` when a recorded run needs to be shared or inspected outside the live workspace.


## Release preflight

Release-mode runs preload a read-only release preflight context built from `lai readiness`, Git state, tags, and Makefile validation targets. This prevents small local models from wasting rounds on ad-hoc runtime probing before a release decision.


Use `lai release-check --json` for a model-free release gate after `lai readiness` reports a clean, ready repository.


## Beta readiness

For beta cuts, use `lai readiness`, `lai release-check --target 0.4.0-beta.4 --json`, `make validate`, and the checks in [Beta readiness](BETA-READINESS.md). The beta gate is deterministic and does not tag, merge, push, upload, or publish artifacts.
