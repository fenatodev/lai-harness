# Runtime and execution model

The runtime has deterministic phases around model calls rather than a free-form autonomous loop.

## High-level lifecycle

1. Resolve configuration and repository state.
2. Load the active spec, mode skill and advisory context metadata when applicable.
3. Reserve aggregate budget counters for rounds, model calls, tool calls, validation, truncation retries and token observations.
4. Call the configured local model server with a bounded schema for the selected mode.
5. Dispatch tool calls through deterministic policy.
6. Record trajectory, audit and metric events.
7. Require validation before claiming success for write flows.
8. Expose review/promotion metadata for safe workspaces.

## Modes and tools

Mode commands get different tool profiles. Read-only modes cannot write. Write modes still use path confinement, symlink protection, pre-write snapshots, post-write validation and policy checks.

Remote work-runs use a work profile that excludes generic host `bash`; `sandbox_exec` exists only inside a verified work-run boundary.

## Trajectory and budget records

Trajectory events are versioned, ordered and metadata-only. They include causal IDs, event type, status, reason code and allowlisted metadata. They do not include raw prompts, stdout, stderr, diffs, secrets, workspace paths or file bodies.

Budget records reserve and consume counters before model/tool/validation work. Unknown token counters remain unknown rather than being coerced to zero.

## Validation

Validation is not implied by a model claim. The harness records explicit validation events and uses post-write gates to prevent early success. See [Testing and validation](TESTING-VALIDATION.md).

## Failure behavior

Critical ambiguity fails closed. Unsupported modes, unsupported adapters, future schemas, missing sandbox images, stale hashes, drifted source state and replay attempts should return explicit errors instead of falling back to a weaker boundary.
