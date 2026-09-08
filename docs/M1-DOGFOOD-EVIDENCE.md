# M1 Dogfood Evidence — structured-context-dogfood

This document records measured dogfood evidence for `.specs/054-structured-context-dogfood.md`.

The evidence is intentionally bounded and public-safe: it records run classes, counters, status, and failure modes without raw private prompts, transcripts, tokens, local network details, or secret values.

## Baseline A — local `plan` with active spec

Task class: identify the next high-value Harness milestone and likely files/tests from the current repository state.

Before M1 changes:

- Run status: failed.
- API calls: 1.
- Tool calls: 1 (`project`).
- Failure: model API rejected the request because the prompt exceeded the 4096-token context window.
- Observed request size: 4700 tokens.

This proved the active spec plus preload/context material was too large before useful reasoning could begin.
After active-spec compaction, reduced AGENTS preload, and a minimal active-spec inspect receipt:

- Run status: completed.
- API calls: 4.
- Tool calls: 3 (`project`, `inspect` active spec, `inspect` `src/local-agent`).
- Failure: none.
- Remaining limits: response truncation occurred twice.
- Compute time: about 294 seconds.

After active-spec plan preflight:

- Run status: completed.
- API calls: 0.
- Tool calls: 0.
- Failure: none.
- Remaining limits: none observed.
- Wall time: about 0.41 seconds.
- Output prioritized `src/`, `tests/`, active-spec/workplan evidence, and validation commands before changelog/roadmap noise.

Outcome: the task improved from context-window failure, through slow model completion, to deterministic completion with no model or tool calls.

## Baseline B — local `diagnose` for readiness/model/MCP

Task class: report readiness, model endpoint, MCP broker readiness, execution policy, branch, and Git clean state without editing files.

Before M1 changes:

- Run status: failed.
- API calls: 1.
- Tool calls: 0.
- Failure: model API rejected the request because the prompt exceeded the 4096-token context window.
- Observed request size: 4635 tokens.
After active-spec compaction alone:

- Run status: failed.
- API calls: 2.
- Tool calls: 4 (`context` operations).
- Failure: model API rejected the request after repeated context discovery.
- Observed request size: 5785 tokens.

After local diagnose fast-path:

- Run status: completed.
- API calls: 0.
- Tool calls: 0.
- Failure: none.
- Compute time: 0.00 seconds in run counters.
- Wall time: about 0.26 seconds.
- Output included readiness, model endpoint, MCP broker status, MCP execution policy, branch, and Git clean summary.

Outcome: the diagnose task improved from context-window failure to deterministic completion with no model or tool calls.

## Current M1 conclusion

M1 has validated three useful changes:

1. Active-spec context must be compact and requirement-preserving.
2. Simple diagnose/status questions should use deterministic preflight instead of model inference.
3. Simple active-spec milestone orientation should use deterministic plan preflight instead of model inference.

Future follow-up work should focus on broader model-backed planning tasks that do not match the narrow preflight conditions.
