# Security model

## Assets and trust boundaries

Protected assets include repository content, credentials accessible to the user, local model API keys, private prompts, logs, state, Git history, and the host operating system. Inputs cross boundaries from the user/gateway into the control plane, from model output into tool arguments, and from the harness into repositories, Docker, the operating system, and the model server.

The user, installed LAI code, configured source repository, local model endpoint, and explicitly configured local sandbox image are assumed trusted. Model output and repository content are not trusted to choose unrestricted actions correctly.

## Implemented controls

- The llama.cpp API key is read from a private external file and sent as a Bearer header.
- `lai serve` uses a separate bearer token, restrictive token-file permissions, loopback-only binding, bounded JSON bodies, serialized asynchronous runs, bounded queue/output, and fixed child process groups.
- Read-only control profiles never receive generic `bash` or file-write tools.
- Beta.15 work profiles (`implement`, `fix`, `refactor`, `ci-fix`) execute only in unique disposable safe workspaces copied from tracked source-repository contents; the source checkout is not their working tree.
- Work profiles never receive generic `bash` or Git mutation tools. They receive repository-confined file tools plus the structured `validate` capability.
- Remote `validate` accepts a small profile rather than a shell command. The harness discovers recognized existing project validation argv and runs it with `shell=False`.
- Remote validation uses a fixed Docker sandbox with `--pull=never`, no network, read-only container root, dropped capabilities, `no-new-privileges`, bounded CPU/memory/PIDs, no host home, no Docker socket, and only the disposable work workspace writable.
- The harness never automatically pulls the sandbox image. Missing Docker/image readiness fails a work run before model execution.
- Promotion is separate from model execution. Only a successful work run may expose a proposal; approval is bound to the SHA-256 of complete patch bytes, not the bounded UI diff.
- Promotion trusts the source baseline captured by the control server before the model starts; mutable workspace metadata must still match that baseline but is never authoritative.
- Before Git mutation, promotion repeats `full` validation in the fixed Docker sandbox and rechecks source SHA, branch, clean status, patch hash, path limits, and target nonexistence.
- Approved patches are applied only to deterministic `lai/promotion-*` feature worktrees. The active source checkout is not switched or edited, and promotion does not commit, push, merge, tag, publish, or call the model.
- File tools resolve targets against the active repository/workspace root; parent and escaping-symlink paths are rejected. Batch patch also validates every replacement before any write.
- The dedicated Git model tool exposes inspection operations only.
- `AGENTS.md` must be read before file edits when present.
- A centralized policy classifies builtin tool actions as `ALLOW`, `ASK`, or `DENY`. Known local Git mutations and dependency installs are `ASK`; selected destructive filesystem/Docker/database/system commands and privilege escalation are `DENY`.
- Validation, acceptance, evidence, debug-evidence, post-patch sanity, stale-write, active-spec, and progress gates constrain write-capable conclusions.
- Recovery checkpoints are stored outside the repository and explicit resume fails closed on branch, Git-status, or tracked-hash drift; prior tool arguments are not replayed.
- Context ranking injects candidate metadata rather than sampled file contents and never bypasses normal inspection/policy.
- Output sizes, file counts, tool rounds, validation duration, control queue length, work diff size, and command durations are bounded.

## What the remote work sandbox does and does not mean

Beta.15 materially isolates remote work execution and adds a hash-bound promotion boundary, but it does not claim complete hostile-code containment. The Docker validation boundary removes network access and ordinary host-secret/daemon exposure and prevents the work child from validating directly in the source checkout. Work results are returned as bounded evidence. Promotion requires an explicit exact hash, repeated sandbox validation, and creates a separate feature worktree rather than modifying the active checkout.

The configured Docker daemon, container runtime, kernel, mounted runtime/dependency directories, and sandbox image remain part of the trusted computing base. Container/kernel escape vulnerabilities, malicious behavior in explicitly mounted dependencies/runtimes, resource-exhaustion bugs outside configured limits, and Docker daemon compromise are outside the guarantees of this project.

The source checkout is still readable by the parent control server when it creates the tracked safe-workspace copy and collects state. Beta.15 does not implement multi-tenant isolation.

## Residual risks

The local interactive `bash` tool remains unsandboxed and runs accepted commands with the LAI user's OS permissions. Command inspection is governance, not complete shell containment: aliases, wrappers, alternate interpreters/executables, shell features, or unlisted commands can bypass intent. This local limitation is why generic `bash` remains absent from all remote control profiles.

Prompt injection from repository files, malicious tracked project code, malicious dependencies invoked by validation, symlink races, endpoint interception on an untrusted network, extension-host compromise, model hallucination, and sensitive content in state/audit/checkpoint/diff output remain possible. Repository filenames/text can bias context ranking; rankings are advisory only. Passing validation proves only the executed checks, not general correctness or security.

## Safe deployment guidance

- Use a dedicated least-privilege account or disposable VM for stronger host isolation.
- Keep secrets outside repositories/workspaces and restrict their filesystem permissions.
- Keep `lai serve` on loopback. Put smartphone/private-network transport behind a separate authenticated gateway/proxy such as the companion gateway + Tailscale Serve.
- Never expose llama.cpp or the control plane directly to the public internet.
- Keep Docker and the configured sandbox image updated and trusted. Do not mount additional host paths casually.
- Review the proposal and exact patch hash before promotion. Promotion creates a dedicated local feature worktree; commit/push/PR remain separate future capabilities.
- Rotate or delete local state/audit/log data according to sensitivity.
- Do not expose LAI as a remote multi-user service without a separate authorization and isolation design.

## Security claims deliberately not made

lai harness does not claim complete shell/container containment, prompt-injection resistance, tenant isolation, deterministic model behavior, proof that passing tests imply safe code, or protection against kernel/container-runtime compromise.

The local Git-mutation policy and its residual limits are documented separately in [Git shell hardening](GIT-SHELL-HARDENING.md).
