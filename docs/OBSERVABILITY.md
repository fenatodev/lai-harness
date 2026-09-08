# Observability

For runtime flow context, see [Runtime execution](RUNTIME-EXECUTION.md).


`lai config` is a deterministic operator diagnostic. It reports effective configuration and path statuses without starting or probing the model server. It prints API key paths and file status only, never secret contents.

lai harness records local operational data under `$LAI_DATA_DIR` (default `~/.local/share/lai`). It does not send these records to a hosted telemetry service.

This is the current operational surface. The [target architecture](TARGET-ARCHITECTURE.md) plans a broader Gateway Run Inspector before broader autonomy. Current metrics, audit, control-run timelines, structured trajectory events, and budget ledger events provide a foundation, not a complete event stream of every action.

## Status and workspace state

`/status` reports the repository, branch, last task/mode, recent and modified files, last validation, Git status, and optional handoff note. State is stored as JSON per workspace. `current-context.md` and `.json` mirror the most recent workspace for cross-agent handoff.

## Runtime checkpoints and recovery

Each non-selection run writes a workspace-scoped JSON checkpoint under `$LAI_DATA_DIR/checkpoints`. Checkpoints are replaced atomically and contain bounded task metadata, lifecycle phase, branch, Git status, tracked-file hashes, and the last tool name. They do not contain replayable tool arguments.

`lai recovery` is deterministic and does not call the model. A non-terminal checkpoint is resumable only when current branch, Git status, and every recorded tracked-file hash still match. `lai resume` creates a new run ID linked to the interrupted run; terminal or drifted checkpoints are not resumed.

`ASK` currently ends a run with `user_action_required`; it is not a suspended tool call that an interface can approve and replay. The authority-intent API can persist and consume a hash-bound approval record, but v1 still does not execute the approved payload. Snapshots and explicit hash-checked file rollback are documented in [Recovery](RECOVERY.md); they do not roll back processes or external effects.

## Context ranking

`lai context <task>` is deterministic and does not call the model. The ranker may inspect Git metadata and bounded local text samples, but it injects only candidate paths, scores, and reason labels. Rankings are advisory and are not persisted as a separate runtime record.

`lai model profile <results.jsonl|latest>` is deterministic and does not call the model. It reads local model-evaluation JSONL evidence and emits a versioned capability profile with explicit `unknown` fields for missing runtime, quantization, template, hardware, suite and repetition data. The recommendation is conservative: no automatic router, no default model change, no model download, and no cloud fallback.

## Metrics

`/metrics` groups recent JSONL events by `run_id` and mode. Events can contain:

- UTC timestamp, run ID, mode, and absolute repository path;
- API duration and token counts reported by the endpoint;
- completion budget and number of supplied tool schemas;
- tool name, duration, and success status.

New metric events declare `schema_version: 1`. Legacy unversioned events remain readable, while unsupported future versions are ignored. The default retention threshold is 5 MB and the default retained tail is 3,000 lines; both are configurable.

These counters are measurements. Current round, timeout, truncation-retry, exploration, and output bounds are separate mechanisms; an aggregate Budget Controller is still planned. Verifier, synthesis, validation, and bounded delegate-wave fixture activity are reported as metadata; future real delegate execution must still reserve budget through the controller before gaining broader authority.

## Forensic audit

`/audit` summarizes the latest run for the current repository. Events associate:

- patch paths and SHA-256 values before and after;
- post-patch sanity status, issue, and hash consistency;
- validation command/result;
- final answer/status when available;
- checkpoint phases, recovery resumes, and blocked recovery attempts.

Audit hashes demonstrate which bytes were observed at stages of a run. They do not prove authorship, safety, completeness, or external timestamp integrity.

The dispatcher records versioned trajectory audit events for model calls, policy decisions, tool completion, and validation tool completion. It also records budget ledger events for reservations, consumption, observations, and exhaustion across rounds, model calls, tool calls, validation calls, truncation retries, and token observations. Unknown token counters remain unknown rather than being coerced to zero. Raw tool arguments are printed to stderr before dispatch. That stream is private operational output, not a sanitized trajectory API.

## Privacy and retention

Runtime records can expose repository names, absolute paths, task descriptions, filenames, snippets of results, commands, validation output, and recovery metadata. Keep the data directory private and outside the repository. Workspace-state, metrics, and audit retention are configurable; JSONL pruning is tail-based and atomic. See [Runtime records](RUNTIME-RECORDS.md) for schema and retention contracts. Avoid entering secrets in prompts. `/clearcontext` clears workspace context, not metrics, audit history, or recovery checkpoints.

## Run history

`lai runs`, `lai run last`, `lai run show <run-id|--last>`, and `lai run tail <run-id|--last>` are deterministic and do not call the model. They read repository-scoped events from the existing metrics and audit JSONL files, optionally enriched by the current checkpoint. Historical events are advisory operational records; inspect current files before using a past run as evidence.

The authenticated control route `GET /v1/runs/<control_run_id>/events` synthesizes a bounded polling timeline from in-memory control-run state. It reports coarse milestones such as queue/start, context loading, workspace preparation, process start, persistence, and completion. It also returns a bounded structured trajectory projection for control-run progress using sequence numbers, event/action/span IDs, reason codes, and allowlisted metadata. Child stdout/stderr is captured after process exit but not copied into events or trajectory records. This route is neither a durable trajectory store nor live model/tool streaming.

The additive local-chat route `GET /v1/local-chat/runs/<control_run_id>/events?client_version=1&cursor=N` exposes the same metadata-only trajectory projection after a client cursor and returns `next_cursor`. It intentionally omits stdout/stderr. Local inspector file content is served through `GET /v1/local-chat/content` as bounded, repository-confined, UTF-8-only, token/secret-pattern-redacted text. Work review is served through `GET /v1/local-chat/runs/<control_run_id>/review` as a sanitized UI projection with changed paths, bounded redacted diff preview, promotion state, lifecycle state, ASK status, validation state and budget projection metadata.

## Readiness

`lai readiness` combines configuration path checks, Git state, server authentication, installed skill status, recovery status, and the latest run summary. It is diagnostic only: it does not call the model, start the server, replay tools, or mutate files.
 Readiness skill records may include capability-declared skill contract metadata, including missing tools/capabilities and authority-claim fields. Those records are diagnostics only; loading a skill never executes hooks or changes the fixed mode tool profile.


## Sanitized run exports

`lai run export <run-id|--last>` writes a local diagnostic bundle derived from metrics, audit events, and checkpoints. The bundle contains `summary.json`, `timeline.jsonl`, and `report.md`. Export records are allowlisted and compacted so raw prompts, full tool outputs, secrets, and unbounded logs are not copied into the bundle.

Future trajectory events need broader artifact references and external-effect receipts, with redaction before persistence or display. Current records already include first trajectory events, budget ledger events, durable approval-intent records, sanitized fake credential receipts, fake external-action receipts, fixture-browser session/download receipts and sandbox-executor metadata. They must preserve local retention controls and must never become instructions or replay authority. See the [autonomy threat model](AUTONOMY-THREAT-MODEL.md).


Session fork experiment records are sanitized local runtime evidence. They include common base metadata, child session IDs, patch hashes, validation status and aggregate cost counters, but not child stdout, stderr, workspace paths, tokens, approvals or process IDs. Historical session content remains untrusted and is not replay authority.
