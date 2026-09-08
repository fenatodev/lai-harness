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
