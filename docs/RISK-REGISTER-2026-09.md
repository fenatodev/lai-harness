# LAI Risk Register — 2026-09

This register tracks the main risks for the September execution block.

Risk status values:

- `open`: needs active attention.
- `watch`: acceptable now, monitor during dogfood.
- `mitigated`: covered by current guardrails.

## RISK-001 — Gateway polish displaces Harness core work

Status: `open`.

Risk: Gateway UI and Telegram improvements are useful, but they can consume time that should go into Harness capability.

Impact: the project looks more finished while the local agent loop remains weaker than it should be.

Mitigation: accept Gateway work only when it supports mobile dogfood of an existing safe Harness capability.

## RISK-002 — MCP authority expands before policy is ready

Status: `open`.

Risk: moving from MCP discovery to tool execution too quickly could expose desktop or file authority through an insufficiently reviewed path.

Impact: local-first privacy and repository safety boundaries weaken.

Mitigation: keep `call-tool` denied until allowlist design, synthetic fixtures, audit, bounded output, timeout handling, and Gateway display rules exist.

## RISK-003 — Context improvements become prompt bloat

Status: `open`.

Risk: context-intelligence work could add more prompt text instead of better selection and summarization.

Impact: local model latency and truncation get worse while appearing more “informed”.

Mitigation: measure tool calls, latency, truncation, and correctness before and after M1 changes.

## RISK-004 — Model switching creates churn

Status: `watch`.

Risk: a new small model may look attractive after one run but perform worse across tool-use, refusal, truncation, or latency cases.

Impact: time is spent changing runtime configuration instead of improving Harness behavior.

Mitigation: keep Ministral as baseline until another model repeatedly beats it on decision-eligible local fixtures.

## RISK-005 — Mobile dogfood hides auth/session failures

Status: `watch`.

Risk: phone workflows can appear ready in health checks but still fail during real session/run/event use.

Impact: the operator discovers broken behavior only during actual use.

Mitigation: M2 must define real mobile scenarios that include pair expiry, session reuse, run creation, event inspection, and recovery.

## RISK-006 — Planning artifacts drift from implementation

Status: `open`.

Risk: plans, specs, and roadmap entries can become stale if implementation changes without updating them.

Impact: future work follows outdated assumptions.

Mitigation: every implementation PR that changes the execution plan should update the related spec, backlog, or decision log.

## RISK-007 — Release ritual starts too early

Status: `watch`.

Risk: merged planning or small operational commits can trigger premature version bump, tag, or release work.

Impact: releases become noisy and less meaningful.

Mitigation: require a release-freeze spec and coherent user-visible theme before release work.
