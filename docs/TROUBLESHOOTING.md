# Troubleshooting

## Server does not start

Run `lai doctor`. Confirm `LAI_HOST`, `LAI_PORT`, the Windows launcher path, and that the selected `llama-server` supports API-key authentication. Inspect private server logs locally; do not paste secrets into issues.

## HTTP 401

Confirm the WSL and Windows key files contain the same value without trailing line breaks. Check `LAI_API_KEY_FILE` and `LAI_API_KEY_FILE_WINDOWS`. Never print the key to diagnose authentication.

## WSL gateway is wrong

Set `LAI_HOST` explicitly. The default is the first gateway from `ip route`, which is common for WSL but not universal. Verify Windows firewall scope before binding beyond loopback.

## PowerShell launcher returns but no server appears

Run the script in a PowerShell terminal to observe its error. Validate `LAI_LLAMA_SERVER`, model access, write access to `LAI_LOG_DIR`, and llama.cpp flags for your build.

## Permission denied for local-agent

Re-run `scripts/install-local.sh` or apply executable permission to the installed file. Copy operations can lose executable metadata; the installer deliberately uses mode 0755.

## Model fails to load

Check available RAM/VRAM, model identifier/path, quantization, context size, and the server log. LAI does not manage model downloads or licenses.

## VS Code does not show @lai

Reload the extension host, confirm the extension activated, and verify its required VS Code engine. Set `lai.agentPath` if the harness is not under `~/.local/bin`.

## Context appears stale

Run `/status`, compare it with `git status`, then use `/clearcontext` if needed. Handoff is advisory and never overrides current files.

## Metrics or audit is empty

Confirm `$LAI_DATA_DIR` is writable. Metrics are created by ordinary runs; audit details are richer for batch-patch implementation runs. `/clearcontext` does not erase either log.


## Configuration fails before runtime

Run `lai config` after editing `config.toml`. Unknown `[lai]` keys, invalid ports, empty required strings, URL-shaped hosts, and non-path values fail before server startup so operator mistakes are caught early.

## Linux or remote server instead of WSL/Windows

Do not use `LAI_WINDOWS_LAUNCHER` for Linux-native or already-running remote servers. Set `LAI_HOST`, `LAI_PORT`, and `LAI_API_KEY_FILE`, then run `lai doctor`. Keep the server private and authenticated.
