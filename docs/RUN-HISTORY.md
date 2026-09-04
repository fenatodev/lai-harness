# run history

`lai runs` lists recent local runs for the current repository from the existing metrics and audit JSONL files.

```bash
lai runs
lai runs --json
```

Use `lai run last` or `lai run show --last` to inspect the most recent recorded run without copying a run ID.

```bash
lai run last
lai run show --last
lai run show --last --json
```

Use `lai run show <run-id>` to inspect one run summary. The summary includes counters, tool usage, policy decisions, validation timeline, modified paths, and the latest failure or stop reason when one exists.

```bash
lai run show 1788502505951-401586
lai run show 1788502505951-401586 --json
```

Use `lai run tail <run-id>` or `lai run tail --last` to inspect a bounded event timeline.

```bash
lai run tail 1788502505951-401586
lai run tail --last --limit 50
```

## behavior

Run history is repository-scoped. Events from other repositories are ignored. The command reads local metrics, audit, and checkpoint records only. It does not call the model, start the model server, replay tool calls, execute shell commands, or mutate files.

The browser is intentionally summary-first. It shows run IDs, mode, status, API/tool counters, token counters, validation counts, policy decisions, phases, modified paths, and validation results when those events exist. It does not treat prior events as current truth; inspect current files before acting on any historical run.

## failure signal

`lai run show` highlights the latest validation failure, agent limit, recovery block, non-success outcome, or failed checkpoint. This is an operational hint for triage, not proof that the current workspace is still broken.
