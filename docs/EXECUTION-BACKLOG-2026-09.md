# LAI Execution Backlog — 2026-09

This backlog turns the September project plan into bounded execution slices.

It is not a wish list. Each item must either improve core Harness capability, support real Gateway dogfood, reduce authority risk, or improve model-evaluation evidence. Anything else waits.

## Current baseline

- Harness stable baseline: `0.4.8`.
- Gateway stable baseline: `0.1.34`.
- Gateway and Harness `main` branches are expected to stay clean, synced, and CI-green before release work.
- Gateway exposes health, mobile, Telegram, model, and MCP foundation visibility.
- MCP tool execution remains denied by default.
- Ministral remains the local model baseline until repeated eval evidence beats it.

## Milestone order

1. `M1 structured-context-dogfood`.
2. `M2 mobile-readonly-dogfood-loop`.
3. `M3 mcp-allowlist-design`.
4. `M4 model-eval-evidence-expansion`.
5. `M5 next-release-freeze`.

Do not skip to MCP execution, mobile write approval, or release ritual before M1 and M2 have produced evidence. M1 and M2 now have evidence; M3 may start only as non-executing allowlist design.

## M1 — structured-context-dogfood

Status: complete in the current planning branch once final milestone validation passes.

Goal: reduce waste in early model rounds by improving deterministic context orientation.

Primary repo: `lai-local-agent`.

Spec candidate: `.specs/054-structured-context-dogfood.md`.

Workplan: [M1 Structured Context Workplan](M1-STRUCTURED-CONTEXT-WORKPLAN.md).

Deliverables:

- Baseline notes for at least two current planning/diagnose tasks.
- Improved metadata-only context summaries or ranking evidence.
- Focused tests for touched context behavior.
- Before/after dogfood or model-eval records.
- Documentation updates only if operator expectations change.

Done means:

- Existing context commands remain model-free.
- Raw source bodies, raw diffs, stdout, stderr, transcripts, credentials, and private paths are still excluded from injected summaries.
- At least one measured task improves tool calls, latency, truncation, or correctness without regression.
- `make check` passes.

Post-M1 follow-up:

- Broaden model-backed planning context only from new measured failures that do not match the narrow active-spec preflight.

## M2 — mobile-readonly-dogfood-loop

M2 status: complete. Implemented in `lai-gateway` PR #42 with sanitized session/run/event payloads and `scripts/mobile-readonly-dogfood.sh`.


Goal: prove the phone/Gateway path can support real read-only project work.

Primary repos: `lai-local-agent` and `lai-gateway`.

Spec candidate: `.specs/055-mobile-readonly-dogfood-loop.md`.

Deliverables:

- Two or three named read-only mobile scenarios.
- Session lifecycle expectations for start, reuse, expiry, and cleanup.
- Sanitized event inspection from the phone path.
- Recovery instructions for expired pair/session state.
- Gateway changes only when they expose existing safe Harness behavior.

Done means:

- A phone user can inspect health, pair, create or select a session, run a read-only task, inspect sanitized status/events, and recover from expiry without reading raw docs.
- No mobile path can request writes, commit, push, release, shell, browser actions, or MCP execution.
- `health-report` remains secret-free.

## M3 — mcp-allowlist-design

Goal: design the first safe step from MCP visibility toward narrow read-only usefulness.

Primary repo: `lai-local-agent`.

Spec candidate: `.specs/056-mcp-allowlist-design.md`.

Deliverables:

- Threat model for one read-only MCP operation class.
- Policy decision table for allow, ask, and deny.
- Audit and bounded-output requirements.
- Synthetic fixtures before any real external tool is called.
- Gateway responsibility notes for displaying policy decisions without broadening authority.

Done means:

- The design can be reviewed without enabling MCP execution.
- `call-tool` remains denied in the default broker foundation.
- A later implementation spec has enough detail to avoid inventing policy during coding.

## M4 — model-eval-evidence-expansion

Goal: keep local model decisions empirical and cheap enough to rerun.

Primary repo: `lai-local-agent`.

Spec candidate: `.specs/057-model-eval-evidence-expansion.md`.

Deliverables:

- Fixtures derived from real dogfood failures.
- Separate tracking for latency, truncation, refusal, tool-call count, and correctness.
- A repeatable baseline record for the current local model.
- A rule for when a candidate model becomes decision-eligible.

Done means:

- Model recommendations are grounded in local records.
- A single promising manual run cannot change the default model.
- Qwen or any other candidate must beat the baseline repeatedly under the hardware budget before adoption.

## M5 — next-release-freeze

Goal: package a coherent user-installable milestone only after evidence exists.

Primary repos: whichever changed during M1-M4.

Deliverables:

- Version target chosen from actual user-visible changes.
- Release notes generated from merged evidence.
- Publication gates green.
- Gateway/Harness compatibility verified by capability contract, not guesswork.
- Explicit statement of what remains deferred.

Done means:

- Release work does not begin just because `main` has commits.
- The release has a coherent theme that a user can understand.
- The release does not claim MCP execution, browser action, learning, or model superiority unless those are actually implemented and validated.

## Stop rules

Stop the current slice when the next action is any of these:

- Cosmetic Gateway polish without a new safe Harness workflow.
- Extra docs that repeat the plan instead of clarifying execution.
- Harness Score work unrelated to product boundaries.
- MCP execution before M3 design is reviewed.
- Release or version bump before a release-freeze spec exists.
- Model switching without repeated eval evidence.

## Promotion rules

A planning item becomes implementation work only when it has:

1. A draft or active spec.
2. A measured failure, dogfood case, or explicit product gap.
3. A bounded validation path.
4. A clear non-goal list.
5. A reason it belongs now instead of later.

If one of those is missing, keep planning instead of coding.
