# Security model

## Assets and trust boundaries

Protected assets include repository content, credentials accessible to the user, local model API keys, private prompts, logs, state, and Git history. Inputs cross boundaries from the VS Code user into the extension, from model output into tool arguments, and from the harness into the operating system and model server.

The user, opened repository, installed LAI code, and local endpoint are assumed trusted. Model output is not trusted to choose unrestricted actions correctly.

## Implemented controls

- API key is read from a private external file and sent as a Bearer header.
- Configuration parsing rejects unknown TOML keys and invalid value types before runtime; diagnostics report secret file status without printing secret contents.
- The reference server launcher refuses builds without API-key support and requests `--no-webui` when available.
- File tools resolve targets against the repository root; parent and escaping-symlink paths are rejected.
- Batch patch additionally refuses every symlink component and validates all replacements before any write.
- The dedicated Git tool exposes status and diff operations only.
- `AGENTS.md` must be read before file edits when present.
- Mode-specific schemas keep write tools away from review/security/plan/debug/test modes.
- A centralized policy classifies every builtin tool action as `ALLOW`, `ASK`, or `DENY`. Known Git mutations and dependency installs are `ASK` and never auto-execute; selected destructive filesystem/Docker/database/system commands and privilege escalation are `DENY`.
- Validation, acceptance, evidence, debug-evidence, and sanity gates constrain conclusions.
- Recovery checkpoints are stored outside the repository and explicit resume fails closed on branch, Git-status, or tracked-hash drift; prior tool arguments are not replayed.
- Context ranking reads only bounded repository samples and injects candidate metadata, not sampled file contents; ranked candidates never bypass normal inspection or policy.
- Output sizes, file counts, tool rounds, and command durations are bounded.

## Residual risks

The `bash` tool is not sandboxed. It uses command inspection to feed the central policy and executes `ALLOW` commands with the LAI user's permissions. Known Git mutations and dependency installs stop at `ASK`; selected destructive patterns stop at `DENY`. Aliases, wrapper scripts, alternate executables, interpreters, shell features, or unlisted commands can still bypass intent. Its working directory is the repository root, but OS-level reads and writes are not confined there.

Model prompt injection from repository files, malicious dependencies invoked by tests, symlink races, endpoint interception on an untrusted network, extension-host compromise, and sensitive content in state/audit/checkpoint output remain possible. Repository filenames and sampled text can also bias context ranking, so rankings remain advisory and require normal evidence inspection. Recovery hashes establish content identity at a checkpoint, not benign behavior or safe intent.

## Safe deployment guidance

- Use a dedicated least-privilege account or disposable VM/container.
- Keep secrets outside the workspace and restrict their filesystem permissions.
- Bind to loopback when server and client share a network namespace. For WSL-to-Windows access, enforce host firewall scope and API authentication.
- Never treat a port binding or API key as proof of internet safety.
- Use only trusted repositories and review commands/diffs.
- Rotate or delete local logs according to their sensitivity.
- Do not expose LAI as a remote multi-user service without a separate authorization and isolation design.

## Security claims deliberately not made

lai harness does not claim complete shell containment, prompt-injection resistance, tenant isolation, deterministic model behavior, or proof that passing tests imply a secure program.

The implemented Git-mutation policy and its residual limits are documented separately in [Git shell hardening](GIT-SHELL-HARDENING.md).
