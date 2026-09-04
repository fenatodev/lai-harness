# lai ↔ codex handoff

LAI maintains a compact handoff so a local bounded task can continue in a higher-context agent, or return later to LAI without reconstructing everything from chat history.

Use:

```text
@lai /handoff Ready for architecture review; validation passed.
```

The generated Markdown includes repository path, branch, last task/mode, recent and modified files, validation, Git status, and an optional note. The JSON form supports tooling.

## Mandatory receiving procedure

Treat handoff files as hints, never as authoritative state. A receiving agent should begin with:

```text
Read ~/.local/share/lai/current-context.md and continue from this state.
Confirm the handoff against current Git and files before modifying anything.
```

Then verify at minimum:

1. repository root and active branch;
2. local versus upstream position;
3. staged, unstaged, and untracked files;
4. relevant file contents;
5. whether reported validation still applies to the current tree.

Do not reset, clean, stash, overwrite, commit, or publish pre-existing work merely because it is absent from or different from the handoff.

## Privacy

The handoff may contain private task text and local paths. Never commit a real `current-context.*`. For examples and tests, use synthetic repositories, branches, names, and results.
