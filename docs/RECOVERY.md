# Runtime recovery

lai harness keeps one versioned recovery checkpoint per workspace under `$LAI_DATA_DIR/checkpoints`.
The checkpoint is operational state, not repository content and not conversation persistence.

## What is recorded

A checkpoint contains bounded data needed to decide whether a fresh run may continue safely:

- schema version and repository root;
- run ID and optional previous run ID;
- mode and bounded task text;
- lifecycle phase and terminal flag;
- current Git branch and short status;
- SHA-256 hashes for files changed or carried across recovery;
- last tool name, but not replayable tool arguments;
- update timestamp and optional terminal reason.

Checkpoint files are written through same-directory temporary files and `os.replace`, so an interruption cannot expose a partially written JSON record as the current checkpoint.

## Inspecting recovery state

Run:

```bash
lai recovery
```

The command does not contact the model. It reports one of:

- `none` — no checkpoint exists for the workspace;
- `interrupted` — a non-terminal checkpoint exists and current evidence still matches;
- `blocked` — the checkpoint is unreadable/incompatible or repository evidence drifted;
- `terminal` — the previous run already completed or ended in another terminal state.

Compatibility compares the repository root, branch, Git status, and every recorded tracked-file hash. Any mismatch blocks resume.

## Explicit resume

When `lai recovery` reports a compatible interrupted run, resume with:

```bash
lai resume
```

Resume starts a new process/run ID. It recovers only the prior mode, task, lifecycle phase, previous run ID, last tool name, and tracked filenames needed for bounded context. It does not replay prior tool calls, commands, edits, approvals, or model messages.

Current repository rules, active spec, policy decisions, live Git evidence, and validation requirements always override checkpoint content.

## Failure behavior

Normal completion marks the checkpoint terminal. `ASK` escalation is terminal as `user_action_required`. Known process failures such as repeated truncation or round-limit exhaustion are finalized as `failed`. A hard interruption that prevents finalization leaves a non-terminal checkpoint for later inspection.

Recovery is not a sandbox, transaction rollback system, or guarantee that interrupted work is semantically correct. It only prevents stale checkpoint state from being resumed silently.
