# M1 Workplan — structured-context-dogfood

This workplan is the implementation-facing plan for `.specs/054-structured-context-dogfood.md`.

## Objective

Improve deterministic context orientation so small local models spend fewer early rounds discovering obvious repository structure.

This milestone should change Harness behavior only after baseline dogfood evidence proves the current context is wasteful.

## Likely code areas

- `src/local-agent`: `repository_context_map`.
- `src/local-agent`: `render_context_map` and prompt renderers.
- `src/local-agent`: `context_checks_payload` and `render_context_checks`.
- `src/local-agent`: `context_symbols_payload` and symbol parsers.
- `src/local-agent`: `rank_context_candidates`.
- `src/lai_semantics.py`: semantic contract references when relevant.

## Likely test areas

- `tests/test_local_agent.py`: context ranking tests.
- `tests/test_local_agent.py`: context map/checks/runs/symbols metadata-only tests.
- `tests/test_local_agent.py`: deterministic context CLI tests.
- `model-eval/fixtures-v1.json`: only if a real dogfood fixture is promoted into model eval.

## Baseline capture before implementation

Capture at least two examples before changing code:

1. `plan` task from a clean repository asking for the next high-value Harness milestone.
2. `diagnose` or `review` task asking for current readiness/model/MCP state.
3. Optional implementation-planning task asking where to modify context-intelligence behavior.

For each baseline, record:

- mode and task class, not full private prompt text;
- tool-call count;
- context tool operations used;
- elapsed time when available;
- truncation or retry count;
- whether the final answer was correct and actionable;
- whether the model requested files or Git evidence that deterministic preflight could have supplied safely.

## Candidate improvements

Prefer these in order:

1. Improve compact prompt summaries of directory groups and changed-path groups.
2. Add subsystem-oriented context hints from existing semantic contracts.
3. Improve symbol summaries for large monolithic files without source bodies.
4. Improve validation/test inventory summaries so the model chooses focused tests earlier.
5. Add recent-run metadata only when it helps explain current failure or readiness.

Avoid these until later:

- embeddings;
- vector indexes;
- background indexing;
- raw file bodies in prompt summaries;
- raw diffs in prompt summaries;
- stdout or stderr in injected summaries;
- private paths;
- speculative model-specific prompting.

## Validation ladder

Use the cheapest reliable loop first:

1. Focused unit tests for touched context functions.
2. Deterministic CLI checks for changed `lai context ... --json` commands.
3. `python3 -m pytest` or `python3 -m unittest` focused on context tests.
4. `make check` after cross-cutting changes.
5. Model-eval or live dogfood comparison only after deterministic tests pass.
6. `make milestone-gate` before integration.

## Current evidence

See [M1 Dogfood Evidence](M1-DOGFOOD-EVIDENCE.md). The completed implementation cut has evidence for two tasks: narrow active-spec `plan` now completes deterministically without model or tool calls, and simple local `diagnose` now completes deterministically without model or tool calls. A future follow-up target is improving broader model-backed planning tasks that do not match these narrow preflight conditions.

## Stop conditions

Stop or re-plan if:

- a change increases prompt size without measurable benefit;
- a change requires raw source bodies or raw diffs in preloaded context;
- a change depends on a specific model quirk;
- the next step is Gateway UI rather than Harness context capability;
- measured correctness gets worse even if latency improves.
