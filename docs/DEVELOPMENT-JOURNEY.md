# Development journey

LAI began as an experiment: could an 8B local model feel useful for real coding work if the agent infrastructure respected its constraints? The answer emerged through profiling and failure-driven engineering rather than a single design pass.

## Prompt bloat and tool loops

General integrations worked, but a large system prompt and many schemas consumed substantial prefill time. A repeated pattern—read one file, infer, read another, infer again—made latency worse. Measurements showed that local responsiveness depended heavily on reducing context and round-trips, not merely shortening the final answer.

Mode-specific skills and tool sets came first. `inspect` then grouped known files into one call, and `patch` grouped exact replacements into one prevalidated operation. A synthetic implementation fixture moved from roughly 14 API calls and 15 tool calls toward 5 API calls and 3 tool calls. The timing improvement was smaller than the round reduction because sanity checking intentionally added work.

## Integration failures

The Windows/WSL launcher initially blocked while PowerShell remained in the critical path. Moving launch behavior out of that path made readiness probing more reliable. During manual iteration, pasting a script containing `set -e` and `exit` into an interactive terminal also closed the session—an operational reminder that installable scripts and pasted command sequences have different failure semantics.

State persistence once failed with `NameError: STATE_BASE` after code was moved without its constant. Another update used `shutil.copy2` in a way that left the installed launcher without the expected executable behavior. Both failures pushed the project toward explicit installation modes, syntax checks, and tests around state/configuration.

The transition to batch patching also exposed an incompatible dispatcher path: defining a tool schema was insufficient when routing, mode allowlists, and post-tool bookkeeping did not all recognize it. Tool additions are now treated as cross-cutting changes with dispatcher and guard coverage.

## From passing tests to sanity

The most instructive latent defect was:

```javascript
throw newError('multiply failed');
```

The available test passed because it did not execute that branch. This led to post-patch sanity: language syntax checks, deterministic analysis of added lines, and a compact model classifier. The point is not that one detector makes code safe; it adds an independent check for defects outside exercised test paths.

## Evidence over plausible prose

Review and security modes sometimes produced reasonable-sounding claims unsupported by the inspected repository. Their skills were tightened around concrete evidence, and a small verification pass was added to filter drafts. Debug received a different constraint: reproduce first, then show the exact value chain—for example `config.timeout → undefined` and `undefined * 1000 → NaN`—before naming a cause.

## Observability and accountability

Performance optimization required API calls, tool calls, tokens, inference duration, and schema counts. Operational accountability required patch paths, hashes, sanity, validation, and terminal state. Metrics and audit JSONL were added progressively, sharing a run ID but serving different questions.

LAI Harness remains experimental. Its contribution is the engineering lesson: small local models can become substantially more useful when their agent harness is designed around constrained context, low schema overhead, fewer inference rounds, concrete evidence, and visible failure modes.
