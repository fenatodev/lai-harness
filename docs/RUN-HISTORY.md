# run history

`lai runs` lists recent local runs for the current repository from the existing metrics and audit JSONL files.

```bash
lai runs
lai runs --json
```

Use `lai run show <run-id>` to inspect one run summary.

```bash
lai run show 1788502505951-401586
lai run show 1788502505951-401586 --json
```

Use `lai run tail <run-id>` to inspect a bounded event timeline.

```bash
lai run tail 1788502505951-401586
lai run tail 1788502505951-401586 --limit 50
```

## behavior

Run history is repository-scoped. Events from other repositories are ignored. The command reads local metrics, audit, and checkpoint records only. It does not call the model, start the model server, replay tool calls, execute shell commands, or mutate files.

The browser is intentionally summary-first. It shows run IDs, mode, status, API/tool counters, token counters, validation counts, policy decisions, phases, and modified paths when those events exist. It does not treat prior events as current truth; inspect current files before acting on any historical run.
