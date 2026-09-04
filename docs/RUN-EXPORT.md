# lai run export

`lai run export` writes a sanitized local diagnostic bundle for a recorded run.

```bash
lai run export --last
lai run export <run-id> --out /tmp/lai-diagnostics
lai run export --last --json
```

The command does not call the model, replay tools, start the server, mutate repository files by default, or publish data. It reads the existing local metrics, audit events, and checkpoint state, then writes a compact bundle.

## Files

- `summary.json`: public run summary, selector, repository, version, event count, and file list.
- `timeline.jsonl`: allowlisted event records with compact commands/results, statuses, phases, decisions, paths, and hashes.
- `report.md`: human-readable summary for debugging or handoff.

## Sanitization

The export intentionally omits raw prompts, full tool arguments, full tool outputs, API keys, and unbounded logs. It is diagnostic evidence, not a replay artifact.
