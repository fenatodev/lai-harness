# Configuration

`lai harness` uses explicit configuration precedence and secret-safe diagnostics.

## Precedence

Configuration is resolved in this order:

1. CLI flags for the current command;
2. environment variables;
3. TOML configuration file;
4. built-in defaults.

The deterministic implementation lives in `src/lai_config.py`; `src/local-agent` keeps compatibility wrappers.

## Files and directories

By default, LAI follows XDG-style locations:

| Type | Default |
| --- | --- |
| Config | `~/.config/lai/` |
| Data/state | `~/.local/share/lai/` |
| Installed binaries | usually `~/.local/bin/` through `install-local.sh` |

Override paths only when you know which process should own that state. Runtime state should not be placed inside the repository.

## Model endpoint

The model server is external. Configure an OpenAI-compatible base URL, model name and API key file/value using `config.example.toml`, environment variables or CLI flags. Do not reuse the control-plane token as the model API key.

```bash
cp config.example.toml ~/.config/lai/config.toml
lai config
lai doctor
```

`lai config` redacts secret values and reports path diagnostics. It should be safe to paste into an issue after reviewing for private paths.

## Control API token

The control plane uses a separate bearer token:

```bash
lai control-token init
lai serve --bind 127.0.0.1 --port 8765
```

Keep the control API bound to loopback. A companion Gateway should keep the token server-side and should not expose it to browser JavaScript or logs.

## Environment hygiene

- Do not put credentials in command arguments when a file or config setting is available.
- Do not copy proxy variables or secret environment into `sandbox_exec`.
- Public diagnostic output must remain secret-free.
- Future unknown config/state schemas fail closed where implemented.

## Verified sandbox image

`LAI_REMOTE_SANDBOX_IMAGE` optionally selects the Docker image used for verified remote work-runs and promotion validation. It must be digest-pinned and already present locally; the harness uses `--pull=never`. Use a Python-capable image because work-run children execute the harness inside the container. `LAI_REMOTE_SANDBOX_PYTHON` defaults to `python3` and accepts only a bare executable name.
