# Installation

## Requirements

- Linux or WSL2;
- Python 3.11 or newer;
- Git and ripgrep (`rg`);
- a running OpenAI-compatible local chat-completions endpoint;
- optionally VS Code with Chat Participant API support for the extension;
- optionally Node.js for JavaScript syntax checks and extension development.

The CLI works without VS Code. The first platform target remains Linux/WSL2. A Gateway-based local web chat uses the separate `lai-gateway` project, while the harness now provides deterministic bootstrap diagnostics for the already-running loopback control endpoint.

## Install the harness

```bash
./scripts/install-local.sh
```

This installs lai harness as `lai`, plus the active internal harness, server helpers, and skills in `~/.local` by default. Override `LAI_BIN_DIR` or `LAI_DATA_DIR` before running the script. Ensure the bin directory is on `PATH`. Tests use temporary overrides and never require changing an active installation.

Create a private API-key file without putting the value in shell history:

```bash
mkdir -p ~/.config/lai
umask 077
read -rsp 'Local llama.cpp API key: ' key_value
printf '%s' "$key_value" > ~/.config/lai/llama-api-key
unset key_value
```

Configuration precedence is:

```text
leading CLI flags > LAI_* environment variables > [lai] in config.toml > defaults
```

The default file is `$XDG_CONFIG_HOME/lai/config.toml`, falling back to `~/.config/lai/config.toml`. Start from `config.example.toml`, then run `lai config` to verify effective values and path diagnostics without contacting the model server. Unknown TOML keys and invalid value types fail closed. Configuration flags must precede the mode, for example:

```bash
lai --config /private/lai.toml --host 127.0.0.1 --port 8080 --doctor
```

Supported settings include:

| Variable | Default | Purpose |
| --- | --- | --- |
| `LAI_HOST` | WSL default gateway | Model-server host |
| `LAI_PORT` | `8080` | Model-server port |
| `LAI_MODEL` | documented Ministral baseline | API model identifier |
| `LAI_API_KEY_FILE` | `~/.config/lai/llama-api-key` | Private llama.cpp key file |
| `LAI_CONTROL_API_KEY_FILE` | `~/.config/lai/control-api-key` | Private `lai serve` bearer-token file |
| `LAI_DATA_DIR` | `~/.local/share/lai` | Skills and runtime records |
| `LAI_CONFIG_DIR` | `~/.config/lai` | Configuration root |
| `LAI_CONFIG_FILE` | `$LAI_CONFIG_DIR/config.toml` | TOML configuration file |
| `LAI_SKILLS_DIR` | `$LAI_DATA_DIR/skills` | Mode skills |
| `LAI_STATE_DIR` | `$LAI_DATA_DIR/state` | Workspace state/handoff source |
| `LAI_METRICS_DIR` | `$LAI_DATA_DIR/metrics` | Metrics JSONL |
| `LAI_AUDIT_DIR` | `$LAI_DATA_DIR/audit` | Audit JSONL |
| `LAI_SERVER_LAUNCHER` | `lai-server-start` | Command invoked when readiness fails |
| `LAI_LLAMA_SERVER` | unset | Server executable passed to the launcher |
| `LAI_API_KEY_FILE_WINDOWS` | unset | Windows path to the llama.cpp key file used by `start-secure.ps1` |
| `LAI_CTX_SIZE` | `4096` in `start-secure.ps1` | Context size passed to Windows `llama-server` |
| `LAI_GPU_LAYERS` | `0` in `start-secure.ps1` | GPU layer count passed to Windows `llama-server` |
| `LAI_PARALLEL` | `1` in `start-secure.ps1` | Parallel slot count passed to Windows `llama-server` |
| `LAI_CHAT_TEMPLATE` | unset | User-supplied authorized template |
| `LAI_MODEL_DEFAULTS_FILE` | `~/.config/lai/model.env` | Optional local defaults file read by `lai-server-start`; only allowlisted `LAI_*` model launcher keys are imported and caller-provided environment variables win |

## llama.cpp on Windows with WSL

For WSL with a Windows-hosted `llama-server`, `scripts/ministral-start` first accepts an already-running authenticated server. When it must start one, it auto-discovers the installed `start-secure.ps1` next to `lai-server-start`, converts the configured key file path for Windows, locates `llama-server.exe` when it is on either WSL or Windows PATH, and injects those values inside PowerShell without printing the key. Set `LAI_WINDOWS_LAUNCHER`, `LAI_LLAMA_SERVER`, or `LAI_API_KEY_FILE_WINDOWS` only when autodiscovery cannot resolve your local setup.

The reference launcher requires `llama-server` support for `--api-key-file`, requests `--no-webui` and metrics when supported, and supports both local GGUF file paths and Hugging Face model identifiers through `LAI_MODEL`. Adjust context and GPU settings for your hardware. Do not reuse an internet-facing bind without firewall and authentication review.

For Linux-native or remote OpenAI-compatible servers, set `LAI_HOST`, `LAI_PORT`, and `LAI_API_KEY_FILE` directly and use `lai doctor` rather than the Windows launcher. The repository intentionally does not include a model or chat template. Supply compatible files under their own license terms.

## Optional local control plane

For the separate Gateway or another private client, initialize a separate control token and start the loopback-only API:

```bash
lai control-token init
lai serve --bind 127.0.0.1 --port 8765
```

Do not reuse the llama.cpp key for this API. The current control plane supports repository-scoped sessions, read-only runs, isolated work runs, cancellation, and separate hash-bound promotion. Remote work requires Docker and the locally available validation image; the harness does not pull it automatically. It does not expose generic remote shell or direct writes to the active checkout. See [Local control plane](CONTROL-PLANE.md) and [Safe workspaces](SAFE-WORKSPACES.md).

The Gateway is installed/configured separately and keeps the harness bearer token server-side. Current v1 capabilities are discoverable with `lai gateway-contract --json`.

Check the local-chat bootstrap without installing optional components or starting a second persistent runtime:

```bash
lai chat-bootstrap --control-url http://127.0.0.1:8765 --json
```

The command reads the existing control token, negotiates `/v1/local-chat/contract`, lists the server-registered workspace/model, reports Linux/WSL2 support, shows whether the model backend and sandbox are ready, and attempts one Safe `plan` chat only when the model endpoint is already authenticated and reachable. Missing Docker or browser support does not block the core chat bootstrap; missing model backend disables only the first-chat attempt. The command does not download models, install Gateway/browser/runtime components, expose tokens, or open a browser.

`install-local.sh` also writes `$LAI_DATA_DIR/distribution/installed-state.json` as schema-versioned local state. The state records the installed component names, current/previous harness version, one-model-runtime policy, publication non-effects and rollback metadata for replaced local artifacts. A repeat install backs up previously installed binaries under `$LAI_DATA_DIR/distribution/rollback/previous` before replacing them.

Inspect the local distribution state without contacting the model or publishing anything:

```bash
lai distribution status --json
```

The distribution diagnostic fails closed when it sees a future state schema and preserves data/config instead of deleting or rewriting unknown state. It does not download a model, install optional Gateway/browser components, start a persistent runtime, create tags, push, publish a VSIX or perform autoupdate.

`install-local.sh` also installs `lai-uninstall`. Running it without flags removes installed binaries and preserves `$LAI_DATA_DIR`, `$LAI_CONFIG_DIR`, and the distribution state; deleting local data/config requires the explicit `--delete-data` flag.

## Extension from source

Open `vscode-extension/` in VS Code Extension Development Host or package it using your normal VS Code extension tooling. No prebuilt VSIX is included. If the harness is not at its default path, set `lai.agentPath` in VS Code settings.

Reload the VS Code window after installation, open a trusted Git repository, and enter `@lai /status`.

## Doctor

With the endpoint running:

```bash
lai doctor
```

Run `lai config` first to inspect effective configuration without printing secrets. Success requires authenticated `/props` to return HTTP 200 while the unauthenticated request does not. The doctor prints status codes, never the key.
