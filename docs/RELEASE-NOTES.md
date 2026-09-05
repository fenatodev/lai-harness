# Release notes

## lai harness v0.4.0-beta.14 — isolated remote work runs

This beta turns the control plane from a read-only mobile analysis surface into a bounded remote work surface without exposing a generic shell or writing directly to the source checkout.

### What changed

- Added remote `implement`, `fix`, `refactor`, and `ci-fix` control runs alongside the existing read-only modes.
- Added a structured `validate` tool with `test`, `check`, `lint`, `build`, `typecheck`, and `full` profiles; callers/models do not provide shell commands.
- Added per-run disposable safe workspaces copied from tracked source-repository contents. Work children execute there rather than in the source checkout.
- Added fixed Docker validation sandboxing with no network, read-only container root, dropped capabilities, `no-new-privileges`, bounded CPU/memory/PIDs, no host home, and no Docker socket.
- Added fail-closed sandbox readiness. The harness never pulls a sandbox image automatically.
- Added bounded work-result evidence: workspace Git status, changed paths, diff, and truncation state.
- Extended existing post-write validation/audit/checkpoint/progress guards so structured validation is first-class evidence.
- `/v1/status` now distinguishes source-repository write posture from disposable-workspace write capability.

### Safety boundary

- No remote mode receives generic `bash`.
- Work runs receive repository-confined file tools plus `validate`; Git mutation tools are absent.
- The source checkout remains unchanged by a work run. Applying/promoting the returned diff is intentionally not implemented in beta.14.
- Clients cannot choose executable, cwd, env, shell text, Docker image, mounts, network settings, or validation argv.
- Remote work is rejected before model execution when Docker or the configured local sandbox image is unavailable.
- Local interactive `bash` remains unsandboxed and is not covered by the remote Docker containment claim.

### Validation evidence

A real Docker smoke on the development machine verified:

```text
exit_code=0
network=blocked
home_secret=hidden
docker_socket=hidden
```

A full remote `implement` smoke with a real control subprocess and Docker validation verified that the isolated workspace changed while the source checkout SHA and files remained unchanged.

### Why this matters

A private PWA or Telegram client can now ask LAI to perform meaningful implementation work, not just analysis. The model can inspect, edit, validate, repair, and return a bounded diff while the irreversible step — applying that diff to the real repository — stays outside the run and can become an explicit approval protocol later.

### Validation gate

```bash
lai release-check --target 0.4.0-beta.14 --json
lai release-pack --target 0.4.0-beta.14 --with-vsix --json
make lint
make check
make test-dev
make test
make harness-score-gate
make validate
```

### Release body for GitHub

lai harness v0.4.0-beta.14 adds isolated remote work runs for `implement`, `fix`, `refactor`, and `ci-fix`. Every remote work run executes in a disposable safe workspace rather than the source checkout, and validation uses a structured profile inside a fixed Docker sandbox with no network, no host home, no Docker socket, dropped capabilities, and a read-only container root.

The control plane still exposes no generic remote shell, Git mutation, direct source-repository write, dependency installation, or release publication. Completed work returns bounded Git/diff evidence for later review/promotion. Existing read-only remote modes remain compatible.

## lai harness v0.4.0-beta.13 — remote capability profiles

Beta.13 added explicit shell-free remote capability profiles and expanded asynchronous control runs to `diagnose` and `release`. Local CLI behavior remained unchanged while control children intersected each mode with a narrower remote tool set before the model received schemas.
