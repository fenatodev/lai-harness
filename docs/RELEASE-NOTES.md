# Release notes

## lai harness v0.4.0-beta.12 — asynchronous read-only control runs

This beta turns the loopback control plane into a useful mobile-facing execution boundary without turning it into a remote shell. Authenticated clients can now submit bounded asynchronous `plan`, `review`, and `security` runs while repository writes and shell-capable modes remain outside the HTTP trust boundary.

### What changed

- Added `POST /v1/runs` for asynchronous `plan`, `review`, and `security` agent runs.
- Added a single serialized worker and a queue of at most four waiting requests.
- Added `GET /v1/runs/<control_run_id>` for queue/running/terminal lifecycle and bounded output.
- Added scoped `DELETE /v1/runs/<control_run_id>` cancellation.
- Child execution uses fixed argv, the current Python/local-agent, repository cwd, stdin disabled, `shell=False`, and a dedicated process group for scoped cancellation.
- Full tasks are not persisted as new control-plane transcript records; public lifecycle records expose task length only.
- Captured stdout/stderr is bounded and reports truncation explicitly.
- Added deterministic fake-process coverage plus a real subprocess smoke against `FakeLlamaServer`.

### Safety boundary

- HTTP model execution is limited to shell-free `plan`, `review`, and `security` modes.
- `diagnose` and `release` remain excluded because their current `bash` surface is not a complete read-only sandbox; generic shell redirection can still mutate the filesystem.
- No HTTP field can select an executable, arbitrary argv, cwd, environment variable, or shell command. Control-run children also refuse implicit model-server autostart.
- No HTTP endpoint writes repository files, mutates Git, installs packages, administers the OS, or publishes releases.
- Queueing is bounded and model work is serialized because the local model is a single scarce resource.
- Loopback-only binding, bearer authentication, request-size limits, no-store responses, and structured JSON errors remain unchanged from beta.11.

### Why this matters

A future Telegram/PWA gateway can now request useful analysis from the PC and poll or cancel it without receiving terminal access. The next write-capable mobile step is not "enable implement"; it is to strengthen the shell boundary and design explicit `ASK` approval objects first.

### Validation gate

```bash
lai control-token status --json
lai release-check --target 0.4.0-beta.12 --json
lai release-pack --target 0.4.0-beta.12 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

### Release body for GitHub

lai harness v0.4.0-beta.12 adds serialized asynchronous control runs for the shell-free `plan`, `review`, and `security` modes. `POST /v1/runs` returns a control-run ID immediately, while authenticated clients can inspect lifecycle/output or cancel that specific run through bounded endpoints.

The worker invokes only the current `local-agent` with fixed argv/cwd and `shell=False`; callers cannot provide a shell command, executable, cwd, environment override, or write-capable mode. `diagnose` and `release` remain intentionally excluded until the shell policy has a stronger structured read-only boundary. Telegram/PWA transport remains a separate gateway project.
