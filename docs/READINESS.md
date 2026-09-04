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
