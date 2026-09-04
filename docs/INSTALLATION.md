# Installation

## Requirements

- Linux or WSL2;
- Python 3.11 or newer;
- Git and ripgrep (`rg`);
- VS Code with Chat Participant API support;
- a running OpenAI-compatible local chat-completions endpoint;
- optionally Node.js for JavaScript syntax checks and extension development.

## Install the harness

```bash
./scripts/install-local.sh
```

This installs `lai`, the active harness, server helpers, and skills in `~/.local` by default. Override `LAI_BIN_DIR` or `LAI_DATA_DIR` before running the script. Ensure the bin directory is on `PATH`. Tests use temporary overrides and never require changing an active installation.

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
| `LAI_API_KEY_FILE` | `~/.config/lai/llama-api-key` | Private key file |
| `LAI_DATA_DIR` | `~/.local/share/lai` | Skills and runtime records |
| `LAI_CONFIG_DIR` | `~/.config/lai` | Configuration root |
| `LAI_CONFIG_FILE` | `$LAI_CONFIG_DIR/config.toml` | TOML configuration file |
| `LAI_SKILLS_DIR` | `$LAI_DATA_DIR/skills` | Mode skills |
| `LAI_STATE_DIR` | `$LAI_DATA_DIR/state` | Workspace state/handoff source |
| `LAI_METRICS_DIR` | `$LAI_DATA_DIR/metrics` | Metrics JSONL |
| `LAI_AUDIT_DIR` | `$LAI_DATA_DIR/audit` | Audit JSONL |
| `LAI_SERVER_LAUNCHER` | `lai-server-start` | Command invoked when readiness fails |
| `LAI_LLAMA_SERVER` | unset | Server executable passed to the launcher |
| `LAI_CHAT_TEMPLATE` | unset | User-supplied authorized template |

## llama.cpp on Windows with WSL

For WSL with a Windows-hosted `llama-server`, copy `scripts/start-secure.ps1` to a private Windows location. In Windows, set `LAI_LLAMA_SERVER`, `LAI_API_KEY_FILE_WINDOWS`, and optionally `LAI_MODEL` and `LAI_LOG_DIR`. In WSL, set `LAI_WINDOWS_LAUNCHER` to that script's Windows path.

The reference launcher requires an API-auth-capable `llama-server`, requests `--no-webui` and metrics when supported, and uses the development profile recorded in the benchmark document. Adjust context and GPU settings for your hardware. Do not reuse an internet-facing bind without firewall and authentication review.

For Linux-native or remote OpenAI-compatible servers, set `LAI_HOST`, `LAI_PORT`, and `LAI_API_KEY_FILE` directly and use `lai doctor` rather than the Windows launcher. The repository intentionally does not include a model or chat template. Supply compatible files under their own license terms.

## Extension from source

Open `vscode-extension/` in VS Code Extension Development Host or package it using your normal VS Code extension tooling. No prebuilt VSIX is included. If the harness is not at its default path, set `lai.agentPath` in VS Code settings.

Reload the VS Code window after installation, open a trusted Git repository, and enter `@lai /status`.

## Doctor

With the endpoint running:

```bash
lai doctor
```

Success requires authenticated `/props` to return HTTP 200 while the unauthenticated request does not. The doctor prints status codes, never the key.
