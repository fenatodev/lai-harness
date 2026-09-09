# Sandbox

The sandbox boundary is implemented for remote work-runs and selected fixtures. It is not a general security promise for all local commands.

## Verified executor

The verified sandbox executor uses Docker with:

- digest-pinned image reference;
- `--pull=never`;
- no network;
- no Docker socket;
- no host home mount;
- no generic runtime or dependency cache mounts;
- non-root user;
- `cap-drop=ALL`;
- `no-new-privileges`;
- read-only root filesystem;
- bounded CPU, memory, PIDs, tmpfs and timeout.

If the required local image is unavailable, the executor fails closed. It does not pull an image or fall back to host execution.

## Local image provisioning

Remote work-runs require a local Docker image reference pinned by digest. The harness does not pull or build that image automatically. Operators may set `LAI_REMOTE_SANDBOX_IMAGE` to a locally available reference such as `python:3.12-bookworm@sha256:<digest>` after provisioning it deliberately.

The value must match `<repository>[:tag]@sha256:<64 lowercase hex>`. Mutable tags such as `python:3.12` or `alpine:latest` are rejected for verified work-runs. The container entrypoint Python defaults to `python3`; `LAI_REMOTE_SANDBOX_PYTHON` may override only a bare executable name, not a path or shell expression.

If Docker is unavailable or the configured digest-pinned image is not present locally, work-runs fail before model execution and do not fall back to host execution.

## Model bridge for work-runs

Work-run children execute inside the no-network Docker sandbox with `LAI_SKILLS_DIR=/workspace/skills`, so installed supervisors use the checked-in skills copied into the disposable workspace. To let them call the configured host model without granting container networking, the control supervisor creates a per-run Unix-domain socket inside the disposable workspace and forwards bounded chat-completion payloads to the trusted host model service. The container receives only `LAI_CONTROL_MODEL_BRIDGE_SOCKET=/workspace/.lai-model-bridge.sock`; model API keys stay on the host side of the bridge and are not mounted into the sandbox. The bridge is removed when the run finishes.

This is not generic egress. `sandbox_exec` and project commands still run with `--network=none` and remain blocked from network clients, proxy configuration, registries and Git remotes.

## `sandbox_exec`

`sandbox_exec` is available only inside verified work-runs. It is not a replacement for host `bash`. It blocks obvious network clients, proxy variables, Git remotes, registry access, system path escape and secret environment inheritance.

Git local operations are allowed only in the safe workspace. Local commits remain visible to review/promotion by comparing against the safe-workspace seed commit.

## Boundaries not provided

- Local CLI modes are not a full OS security sandbox.
- The model server is not sandboxed by this repository.
- Real browser automation is not enabled.
- Real MCP servers are not started from repository config.
- Real external accounts and credentials are disabled.

Use OS/container isolation and least privilege when running untrusted projects.
