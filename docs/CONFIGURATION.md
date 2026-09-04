# Configuration

LAI reads configuration from leading CLI flags, `LAI_*` environment variables, `[lai]` in `config.toml`, then defaults. This precedence is strict: CLI wins over environment, environment wins over TOML, and TOML wins over defaults.

Run a deterministic configuration report with:

```bash
lai config
```

The report does not call or start the model server. It prints effective values and path status checks. API key contents are never printed.

## TOML schema

`config.toml` supports only the `[lai]` table and these keys:

- `host`
- `port`
- `model`
- `api_key_file`
- `data_dir`
- `skills_dir`
- `state_dir`
- `metrics_dir`
- `audit_dir`
- `llama_server`
- `server_launcher`
- `chat_template`

Unknown keys fail closed. `config_dir` and `config_file` are selected before the TOML file is read, so they must be supplied by CLI flags or environment variables rather than inside `[lai]`.

## Validation

`port` must be an integer from 1 to 65535. `model` and `server_launcher` must be non-empty strings. `host` may be unset for automatic gateway detection, but if set it must be a hostname or IP address, not a URL or path. Filesystem values must be non-empty path strings.

Missing directories or optional files are diagnostics, not fatal errors for deterministic commands. Runtime commands may still fail later when a required server, executable, template, or API key file is absent.

## Server workflow

For WSL with a Windows-hosted `llama-server`, the WSL launcher calls `powershell.exe` with `scripts/start-secure.ps1`. Set `LAI_WINDOWS_LAUNCHER` in WSL and set `LAI_LLAMA_SERVER`, `LAI_API_KEY_FILE_WINDOWS`, and optional model/log settings in Windows.

For Linux-native or remote OpenAI-compatible servers, set `LAI_HOST`, `LAI_PORT`, and `LAI_API_KEY_FILE` directly and run `lai doctor`. Do not expose a server beyond loopback or a private network without firewall and authentication review.
