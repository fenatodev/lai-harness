# Troubleshooting

Use this guide for current post-A12 behavior. Do not paste secrets, private paths, real prompts, customer data, audit logs or model files into public issues.

## Start with deterministic diagnostics

```bash
lai readiness
lai config
lai validation matrix
lai gateway-contract --json
```

These commands do not require a model response and should be the first evidence collected for most issues.

## Model endpoint fails

Run:

```bash
lai doctor
```

Check host, port, model name, context size, API key file, server logs and whether the server is OpenAI-compatible. The model server is external to this repository. `lai harness` does not download models or manage model licenses.

## HTTP 401 or control-plane auth failure

Separate the two credential classes:

- the model API key authenticates the local model server;
- the control token authenticates `lai serve`.

Initialize the control token with:

```bash
lai control-token init
lai serve --bind 127.0.0.1 --port 8765
```

Do not print tokens while debugging.

## Local-chat or Gateway connection fails

Run:

```bash
lai chat-bootstrap --control-url http://127.0.0.1:8765 --json
```

Expected failure classes include missing model backend, missing sandbox image, unsupported client version, non-loopback URL, missing CSRF on POST, unregistered workspace or unsupported model ID. The Gateway is a companion and must keep the control token server-side.

## Work-run or sandbox fails

Remote work-runs require the verified sandbox executor. Common causes:

- required digest-pinned Docker image is not present locally;
- `LAI_REMOTE_SANDBOX_IMAGE` is unset, still points at the placeholder default, is not digest-pinned, or references an image that `docker image inspect` cannot find;
- Docker is unavailable to the current user;
- command attempts network, registry, proxy, host path or Git remote access;
- `sandbox_exec` is invoked outside a verified work-run.

The executor fails closed. It does not pull images or fall back to host execution.

## Promotion fails

Promotion requires exact source state, validation evidence and `patch_sha256`. Recompute review metadata and retry only when the new hash is intentional. Stale hashes, dirty source checkout and source drift are expected blocking conditions.

## Distribution status fails with future schema

`lai distribution status` fails closed when `$LAI_DATA_DIR/distribution/installed-state.json` uses an unknown future schema. This preserves data. Inspect the file locally, back it up if needed and avoid deleting state unless you intentionally use uninstall with `--delete-data`.

## MCP, browser or external actions appear unavailable

That is usually correct for the current package:

- generic MCP `call-tool` remains denied;
- MCP execution is limited to `fixture_stdio` `write_artifact`;
- browser support is `fixture_browser` only;
- real credentials and real external accounts are disabled;
- fake Git remote actions are receipts, not GitHub pushes.

## Context seems wrong or stale

Use:

```bash
lai context map
lai context changes
lai context graph --json
lai context runs
```

Context metadata is advisory. Inspect actual files before relying on it. Code graph is Python AST only and can report heuristic or unknown edges.

## Installed command is missing or not executable

Re-run:

```bash
./scripts/install-local.sh
```

The installer uses executable permissions and records local distribution state. To remove installed files while preserving data/config:

```bash
lai-uninstall
```

## Validation fails

Read the first failing boundary. Do not weaken tests to make a bad implementation pass. For documentation-only changes, start with link/static checks and `make check`. For runtime/security/distribution boundaries, use the relevant focused tests and the broader gates described in [Testing and validation](TESTING-VALIDATION.md).
