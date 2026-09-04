# Observability

LAI records local operational data under `$LAI_DATA_DIR` (default `~/.local/share/lai`). It does not send these records to a hosted telemetry service.

## Status and workspace state

`/status` reports the repository, branch, last task/mode, recent and modified files, last validation, Git status, and optional handoff note. State is stored as JSON per workspace. `current-context.md` and `.json` mirror the most recent workspace for cross-agent handoff.

## Runtime checkpoints and recovery

Each non-selection run writes a workspace-scoped JSON checkpoint under `$LAI_DATA_DIR/checkpoints`. Checkpoints are replaced atomically and contain bounded task metadata, lifecycle phase, branch, Git status, tracked-file hashes, and the last tool name. They do not contain replayable tool arguments.

`lai recovery` is deterministic and does not call the model. A non-terminal checkpoint is resumable only when current branch, Git status, and every recorded tracked-file hash still match. `lai resume` creates a new run ID linked to the interrupted run; terminal or drifted checkpoints are not resumed.

## Metrics

`/metrics` groups recent JSONL events by `run_id` and mode. Events can contain:

- UTC timestamp, run ID, mode, and absolute repository path;
- API duration and token counts reported by the endpoint;
- completion budget and number of supplied tool schemas;
- tool name, duration, and success status.

When the metrics file exceeds roughly 5 MB, the harness retains its most recent 3,000 lines. This is a size guard, not a complete retention policy.

## Forensic audit

`/audit` summarizes the latest run for the current repository. Events associate:

- patch paths and SHA-256 values before and after;
- post-patch sanity status, issue, and hash consistency;
- validation command/result;
- final answer/status when available;
- checkpoint phases, recovery resumes, and blocked recovery attempts.

Audit hashes demonstrate which bytes were observed at stages of a run. They do not prove authorship, safety, completeness, or external timestamp integrity.

## Privacy and retention

Runtime records can expose repository names, absolute paths, task descriptions, filenames, snippets of results, commands, validation output, and recovery metadata. Keep the data directory private, outside the repository, exclude it from version control, and delete or rotate records according to project policy. Avoid entering secrets in prompts. `/clearcontext` clears workspace context, not metrics, audit history, or recovery checkpoints.
