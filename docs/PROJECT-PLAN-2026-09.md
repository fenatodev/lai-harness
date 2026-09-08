# LAI Project Plan — 2026-09

This planning document captures the next execution plan for `lai harness`, `lai-gateway`, and the adjacent automation companion after the stable `v0.4.8` Harness baseline and the `v0.1.34` Gateway baseline.

It is intentionally narrower than the roadmap. The roadmap says what may exist later; this plan says what should absorb project time next.

See [Execution Backlog — 2026-09](EXECUTION-BACKLOG-2026-09.md) for milestone IDs, dependencies, done criteria, and stop rules.

See [Decision Log — 2026-09](DECISION-LOG-2026-09.md) for the current project choices that should prevent scope churn.

See [Risk Register — 2026-09](RISK-REGISTER-2026-09.md) for risks that should shape milestone sequencing.

See [Planning Manifest — 2026-09](PLANNING-MANIFEST-2026-09.json) for a machine-readable summary of milestones, stop rules, and the next action.

See [M1 Structured Context Workplan](M1-STRUCTURED-CONTEXT-WORKPLAN.md) for the implementation-facing plan for the recommended next milestone.

## Current state

- Harness `main` is stable at `0.4.8` with post-release fixes merged for bounded model API errors and strict chat-template remote diagnose runs.
- Gateway `main` is stable at `0.1.34` with compact health reporting, mobile/private status, Telegram delivery, MCP foundation visibility, and single-runtime model hygiene.
- Local dogfood validated a single `llama-server` runtime on the Harness model endpoint; duplicate Gateway model runtimes were eliminated.
- MCP is configured and visible locally as a non-executing broker foundation. `call-tool` remains denied.
- Mobile and Telegram paths are usable for health reporting and read-only control-plane visibility, but they are still operator tools, not a complete product loop.

## Planning principle

The project should now prioritize core LAI capability over Gateway polish.

Gateway work remains valuable only when it reduces friction for Harness dogfood, exposes existing safe Harness capability, or makes operational safety clearer. Visual polish without a core capability behind it is deferred.

## Priority stack

### P0 — Preserve the stable base

Goal: keep Harness and Gateway ready for real use while new work happens.

Required behavior:

- Keep Harness `main` and Gateway `main` clean, synced, and CI-green before starting any release path.
- Keep one local model runtime as the default operational posture; do not reintroduce a second persistent Gateway model server.
- Keep remote control profiles shell-free unless a dedicated threat model, spec, and validation plan exists.
- Keep MCP `call-tool` denied until allowlisted execution has policy, audit, UI, tests, and dogfood evidence.
- Keep Telegram/mobile paths secret-free: no bearer token, pair token, chat id, model API key, local private path, or raw transcript in UI, CLI, logs, or notifications.

Exit condition:

- `health-report` is `ready`, stack compatibility is `ready_for_local_commit`, and RAM/model runtime checks show no duplicate model server.

### P1 — Core context intelligence

Goal: make LAI better at choosing what to inspect before inference, especially on constrained local models.

Next work items:

1. Improve structured repository maps so the model sees subsystem boundaries before it asks for files.
2. Add richer symbol summaries for Python and JavaScript without source bodies.
3. Add compact process/test/runtime views that summarize evidence without stdout/stderr dumps.
4. Expand context-ranking fixtures from real dogfood failures instead of speculative examples.
5. Measure whether context changes reduce tool calls, truncation, and runtime latency in fixed model-eval tasks.

Not in scope yet:

- Embeddings, vector databases, external indexing services, or persistent semantic indexes.
- “Learning” that silently changes behavior without versioned evidence and review.
- Broad background scanning of user files.

Definition of done:

- A dedicated spec exists.
- Focused fixtures prove better ranking on observed failures.
- `make check` passes.
- Model-eval records show equal or fewer tool calls or lower latency on at least one decision-eligible fixture without worse correctness.

### P2 — Real mobile dogfood loop

Goal: make the phone/Gateway path useful for actual project work, not only health checks.

Next work items:

1. Define two or three safe recurring dogfood scenarios, such as status review, release-readiness review, and read-only planning from current repository state.
2. Improve session lifecycle quality: clear session naming, stale-session cleanup guidance, and compact session summaries.
3. Add bounded UI affordances only when they expose existing safe Harness capabilities.
4. Ensure every phone path keeps credentials server-side or page-memory-only and never stores secrets in browser storage.
5. Capture dogfood failures as Harness/Gateway fixtures before adding new capabilities.

Not in scope yet:

- Mobile write approval, commit, push, PR, release, MCP tool execution, or browser actions.
- Automatic notification loops that run without explicit operator scheduling or opt-in.

Definition of done:

- A phone user can pair, inspect health, create/read a session, run a read-only control task, inspect sanitized events, and recover from expired pairing without reading raw docs.

### P3 — Governed MCP evolution

Goal: move from MCP visibility to safe, allowlisted usefulness without granting broad desktop authority.

Next work items:

1. Keep the current non-executing MCP broker as the default.
2. Design an allowlist model for one narrow read-only tool class first.
3. Add policy decisions, audit events, bounded output, timeout handling, and explicit denial evidence.
4. Add Gateway UI only for classification and later explicit approval, never silent execution.
5. Dogfood with synthetic fixtures before touching a real desktop command path.

Not in scope yet:

- Arbitrary MCP `call-tool` execution.
- Shell execution through MCP.
- File mutation or process control from mobile.
- Any MCP server that requires exposing credential values to the model or UI.

Definition of done for the first execution milestone:

- One allowlisted read-only operation works through policy and audit.
- All non-allowlisted operations fail closed.
- Output is bounded and secret-free.
- Gateway cannot broaden the request beyond what Harness policy allows.

### P4 — Model evaluation and baseline discipline

Goal: keep local model choices empirical.

Next work items:

1. Convert every real model failure into a small, repeatable fixture when possible.
2. Track latency, truncation, refusal, tool-call count, and correctness separately.
3. Keep Ministral as the baseline until another model under the local hardware budget repeatedly beats it on decision-eligible tasks.
4. Retest alternatives only when a candidate is likely to improve the current bottleneck.

Not in scope yet:

- Default model changes from one good-looking manual run.
- Download automation or model redistribution.
- Benchmark theater that does not affect Harness/Gateway decisions.

Definition of done:

- Model recommendations cite local eval records, not preference or hype.

## Explicit de-prioritization

Do not spend the next project block on these unless they unblock a higher-priority item:

- Additional Gateway visual polish after the health card work.
- New Telegram convenience buttons that do not expose a new safe Harness workflow.
- Version bumps, tags, or releases without a coherent user-installable milestone.
- Harness Score chasing for subagents or MCP env interpolation when it does not match the product boundary.
- Broad “self-improvement” features without versioned records, deterministic evaluation, rollback, and operator review.
- Commercial automation features inside the Harness repository.

## Suggested next milestone

The next milestone should be a Harness milestone, not a Gateway milestone.

Name: `structured-context-dogfood`

Primary outcome:

- LAI should use better deterministic context views before model inference so small local models spend fewer rounds discovering obvious repository structure.

First spec candidate:

- `054-structured-context-dogfood.md`

First acceptance target:

- For at least two observed planning/diagnose tasks, the harness should provide enough structured context that the model needs fewer file-inspection or Git-discovery tool calls while preserving correctness.

## Recommended execution order

1. Create the `054-structured-context-dogfood` spec.
2. Reproduce two current local tasks where context discovery is still wasteful.
3. Add or improve deterministic context summaries.
4. Add fixtures that prove the ranking/summary improvement.
5. Run model-eval before and after the change.
6. Only then decide whether Gateway needs any UI change to expose the result.

## Planning guardrail

When tempted to add a feature, ask which class it belongs to:

- Core capability: improves the harness reasoning/execution loop.
- Control surface: exposes existing safe capability to a human operator.
- Safety/observability: reduces hidden failure or authority risk.
- Cosmetic polish: improves appearance but not the work loop.

For the next block, accept core capability and safety/observability. Reject cosmetic polish. Control-surface work must prove it helps dogfood a core capability.

## Baseline context evidence for the next milestone

Current deterministic context commands already expose useful metadata:

- `lai context map --json` reports 149 tracked files and grouped repository structure.
- `lai context checks --json` reports 15 test files plus Makefile targets such as `test`, `check`, `validate`, and `milestone-gate`.
- `lai context runs --json` reports 121 recent run records/checkpoints as metadata-only orientation.

This means the next milestone should not simply add more raw context. It should improve selection, summarization, and measurement.

Candidate dogfood tasks:

1. Planning task: from a clean repo, identify the next high-value Harness milestone without reading broad docs repeatedly.
2. Diagnose task: explain current readiness/model/MCP state without triggering unnecessary model rounds or verbose discovery.
3. Implementation task: locate the right context-ranking files/tests for a narrow context-intelligence change with fewer inspect/search cycles.

Success metric:

- Fewer early discovery calls for the same answer quality.
- Lower latency or fewer truncation retries on the same local model.
- No expansion of authority or secret exposure.
