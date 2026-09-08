# Spec: model eval evidence expansion

## Metadata

- Mode: `full`
- Status: `draft`

## Goal

Make local model decisions evidence-driven by turning observed dogfood failures into repeatable evaluation fixtures.

The milestone should improve decision quality without changing the default model.

## Requirements

### REQ-001

Select dogfood failures that are small enough to become repeatable fixtures and relevant enough to affect Harness/Gateway decisions.

### REQ-002

Record latency, truncation/retry behavior, refusal behavior, tool-call count, and correctness separately.

### REQ-003

Define what makes a candidate model decision-eligible under the local hardware budget.

### REQ-004

Preserve Ministral as the baseline until a candidate repeatedly beats it on decision-eligible fixtures.

### REQ-005

Prevent model-eval records from storing prompts, credentials, private paths, raw transcripts, or unbounded outputs.

### REQ-006

Document any recommendation as evidence-based, including what the evidence does not prove.

## Acceptance Criteria

- At least one new fixture comes from a real dogfood failure.
- Existing model-eval behavior remains deterministic and secret-free.
- The default model is unchanged by this planning milestone.
- Candidate model evaluation cannot pass based on one manual run.
- Documentation states when evidence is insufficient.

## Validation

- Focused model-eval tests for any changed fixture or scoring behavior.
- `make check` before integration.
- Local model-eval dogfood only when a repeatable fixture exists.
- Publication scan for generated records and docs.

## Context and Constraints

Qwen dogfood did not clear the bar for the current milestone. The project should not churn between models unless the measured failure mode points at model capability rather than prompt/context/tooling defects.

## Non-Goals

- Changing the default model.
- Downloading or redistributing model files.
- Adding benchmark theater that does not change a product decision.
- Treating leaderboard claims as local evidence.
- Expanding context or authority solely to help a model pass a fixture.

## Implementation Notes

Prefer fixtures that expose actionable Harness improvements: context selection, refusal handling, truncation handling, tool schema pressure, or strict chat-template compatibility.

## Traceability

- `REQ-001` -> selected dogfood fixture notes.
- `REQ-002` -> eval record fields/tests.
- `REQ-003` -> decision eligibility rule.
- `REQ-004` -> baseline comparison record.
- `REQ-005` -> secret-free persistence tests.
- `REQ-006` -> documentation of recommendation limits.
