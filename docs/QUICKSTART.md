# Quick start

This guide starts from a clean checkout and avoids optional components until they are needed.

## 1. Clone and inspect

```bash
git clone https://github.com/fenatodev/lai-harness.git
cd lai-harness
./src/lai --help
./src/lai readiness
./src/lai config
```

These commands are deterministic and do not require a model server.

## 2. Inspect validation policy

```bash
./src/lai validation matrix
```

The matrix reports what checks are required for each risk class. It does not execute checks or weaken existing gates.

## 3. Configure a local model endpoint

Copy the sample config or use environment variables:

```bash
cp config.example.toml ~/.config/lai/config.toml
./src/lai config
./src/lai doctor
```

The model server is external to this repository. It must be OpenAI-compatible and authenticated according to your local configuration.

## 4. Install the local wrapper

```bash
./scripts/install-local.sh
lai --help
lai readiness
```

The installer copies the standard-library runtime and wrapper. It does not install Python packages, download models, start a browser or publish artifacts.

## 5. Start the control plane

```bash
lai control-token init
lai serve --bind 127.0.0.1 --port 8765
```

Keep this bound to loopback unless a separately reviewed boundary exists.

## 6. Bootstrap local-chat

In another terminal:

```bash
lai chat-bootstrap --control-url http://127.0.0.1:8765 --json
```

`chat-bootstrap` negotiates `/v1/local-chat/contract`, checks registered workspaces and the default model, reports sandbox readiness and attempts a first Safe `plan` chat only when the model backend is reachable.

## 7. First safe workflow

A conservative first interaction is read-only:

```bash
lai plan "Summarize the repository status and suggest the next validation step."
```

For code changes, use a dedicated branch or safe workspace, inspect the diff and validate before any Git publication. Control-plane work-runs produce review/promotion proposals rather than writing directly to the source checkout.

## 8. Uninstall

```bash
lai-uninstall
```

By default, uninstall removes installed binaries and preserves configuration, data and distribution state. Use `--delete-data` only when you intentionally want local state removed.
