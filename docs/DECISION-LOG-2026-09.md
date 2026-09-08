# LAI Decision Log — 2026-09

This log records planning decisions for the September execution block. It is intentionally compact and should only capture choices that prevent churn.

## DEC-001 — Prioritize Harness core over Gateway polish

Decision: the next project block should focus on Harness context intelligence before further Gateway UI polish.

Reason: Gateway health, mobile, Telegram, model, and MCP visibility are already usable enough for current dogfood. Additional UI polish has lower leverage than improving the local model work loop.

Implication: Gateway changes are accepted only when they expose existing safe Harness capability, reduce dogfood friction, or improve safety/observability.

## DEC-002 — Keep MCP execution denied for now

Decision: MCP remains a non-executing broker foundation until an allowlist design is reviewed and tested.

Reason: the current MCP boundary deliberately reports config and policy classification without starting servers or calling tools. Broad desktop authority is too risky without policy, audit, bounded output, timeout handling, and Gateway display rules.

Implication: `.specs/056-mcp-allowlist-design.md` is design work only. Any execution milestone must be separate.

## DEC-003 — Treat model switching as evidence-gated

Decision: Ministral remains the default local model baseline until another candidate repeatedly beats it on decision-eligible fixtures under the local hardware budget.

Reason: Qwen dogfood did not clear the current bar, and one-off model impressions are not reliable enough to justify churn.

Implication: model-eval expansion should improve evidence before changing defaults.

## DEC-004 — Prefer measured context improvement over larger prompts

Decision: the next context milestone should improve selection, summarization, and measurement rather than injecting more raw text.

Reason: current context commands already expose useful metadata. The bottleneck is choosing and presenting the right evidence to a constrained local model, not simply increasing prompt size.

Implication: `.specs/054-structured-context-dogfood.md` must start with baseline dogfood cases and measured before/after evidence.

## DEC-005 — Do not start release work yet

Decision: no new Harness or Gateway release should start from the current planning branch.

Reason: the current changes are planning artifacts, not a user-installable runtime milestone.

Implication: a future release-freeze spec is required before tag, release notes, or publication work.
