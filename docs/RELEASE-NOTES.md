# Release notes

## lai harness v0.4.0-beta.13 — remote capability profiles

This beta expands useful smartphone-facing analysis without expanding the remote trust boundary. Authenticated control clients can now run `diagnose` and `release` in addition to `plan`, `review`, and `security`, but control children never receive shell or write tool schemas.

### What changed

- Added explicit local-vs-remote tool capability maps instead of relying on a shared mode schema.
- Added remote `diagnose` and `release` asynchronous runs.
- Remote `diagnose`/`release` receive only `project`, `read`, `inspect`, `search`, `list`, and read-only `git`.
- Control-run lifecycle records report the `shell-free-read-only` tool profile.
- `/v1/status` reports the remote profile and five allowed remote modes.
- Added fake-model request inspection proving forbidden schemas are absent before inference.

### Safety boundary

- Local `diagnose` and `release` retain their existing `bash` tool; remote control children do not.
- `bash`, `edit`, `create`, `patch`, and `rewrite` are forbidden from every remote capability profile.
- `implement`, `fix`, `ci-fix`, `refactor`, `debug`, `test`, and general mode remain rejected by the control API.
- No HTTP field selects a command, executable, argv prefix, cwd, or environment override.
- No HTTP endpoint performs Git mutation, repository writes, dependency installation, OS administration, or release publication.
- The existing local `bash` policy is still not claimed to be a complete sandbox.

### Why this matters

A future Telegram/PWA gateway can now ask the PC to diagnose problems and evaluate release readiness without receiving terminal access. Capability reduction happens before the model receives tool schemas, so prompt injection cannot request a tool that is absent from the remote profile.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.13 --json
lai release-pack --target 0.4.0-beta.13 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

### Release body for GitHub

lai harness v0.4.0-beta.13 adds explicit shell-free remote capability profiles and expands asynchronous control runs to `diagnose` and `release`. Local CLI behavior remains unchanged, while control children intersect each mode with a narrower remote tool set before the model receives schemas.

Remote `diagnose`/`release` can inspect project state, repository files and Git evidence, but receive no `bash` or write tools. The control API remains loopback-only, bearer-authenticated, bounded, serialized and unable to accept caller-controlled commands, executables, cwd or environment overrides. Telegram/PWA transport remains a separate gateway project.
