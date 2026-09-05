# Observability

`lai config` is a deterministic operator diagnostic. It reports effective configuration and path statuses without starting or probing the model server. It prints API key paths and file status only, never secret contents.

lai harness records local operational data under `$LAI_DATA_DIR` (default `~/.local/share/lai`). It does not send these records to a hosted telemetry service.

## Status and workspace state

`/status` reports the repository, branch, last task/mode, recent and modified files, last validation, Git status, and optional handoff note. State is stored as JSON per workspace. `current-context.md` and `.json` mirror the most recent workspace for cross-agent handoff.

## Runtime checkpoints and recovery

Each non-selection run writes a workspace-scoped JSON checkpoint under `$LAI_DATA_DIR/checkpoints`. Checkpoints are replaced atomically and contain bounded task metadata, lifecycle phase, branch, Git status, tracked-file hashes, and the last tool name. They do not contain replayable tool arguments.

`lai recovery` is deterministic and does not call the model. A non-terminal checkpoint is resumable only when current branch, Git status, and every recorded tracked-file hash still match. `lai resume` creates a new run ID linked to the interrupted run; terminal or drifted checkpoints are not resumed.

## Context ranking

`lai context <task>` is deterministic and does not call the model. The ranker may inspect Git metadata and bounded local text samples, but it injects only candidate paths, scores, and reason labels. Rankings are advisory and are not persisted as a separate runtime record.

## Metrics

`/metrics` groups recent JSONL events by `run_id` and mode. Events can contain:

- UTC timestamp, run ID, mode, and absolute repository path;
- API duration and token counts reported by the endpoint;
- completion budget and number of supplied tool schemas;
- tool name, duration, and success status.

New metric events declare `schema_version: 1`. Legacy unversioned events remain readable, while unsupported future versions are ignored. The default retention threshold is 5 MB and the default retained tail is 3,000 lines; both are configurable.

## Forensic audit

`/audit` summarizes the latest run for the current repository. Events associate:

- patch paths and SHA-256 values before and after;
- post-patch sanity status, issue, and hash consistency;
- validation command/result;
- final answer/status when available;
- checkpoint phases, recovery resumes, and blocked recovery attempts.

Audit hashes demonstrate which bytes were observed at stages of a run. They do not prove authorship, safety, completeness, or external timestamp integrity.

## Privacy and retention

Runtime records can expose repository names, absolute paths, task descriptions, filenames, snippets of results, commands, validation output, and recovery metadata. Keep the data directory private and outside the repository. Workspace-state, metrics, and audit retention are configurable; JSONL pruning is tail-based and atomic. See [Runtime records](RUNTIME-RECORDS.md) for schema and retention contracts. Avoid entering secrets in prompts. `/clearcontext` clears workspace context, not metrics, audit history, or recovery checkpoints.

## Run history

`lai runs`, `lai run last`, `lai run show <run-id|--last>`, and `lai run tail <run-id|--last>` are deterministic and do not call the model. They read repository-scoped events from the existing metrics and audit JSONL files, optionally enriched by the current checkpoint. Historical events are advisory operational records; inspect current files before using a past run as evidence.


## Readiness

`lai readiness` combines configuration path checks, Git state, server authentication, installed skill status, recovery status, and the latest run summary. It is diagnostic only: it does not call the model, start the server, replay tools, or mutate files.


## Sanitized run exports

`lai run export <run-id|--last>` writes a local diagnostic bundle derived from metrics, audit events, and checkpoints. The bundle contains `summary.json`, `timeline.jsonl`, and `report.md`. Export records are allowlisted and compacted so raw prompts, full tool outputs, secrets, and unbounded logs are not copied into the bundle.
