# Spec: model eval evidence expansion

## Metadata

- Mode: `full`
- Status: `complete`

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
- Unsupported validation-tool recommendations are machine-detectable in fixture output.
- Refusal/disclaimer behavior is recorded separately from hallucination flags.
- Existing model-eval behavior remains deterministic and secret-free.
- The default model is unchanged by this planning milestone.
- Candidate model evaluation cannot pass based on one manual run.
- Documentation states when evidence is insufficient.

## Validation

- `REQ-001`: inspect `model-eval/fixtures-v1.json` and `docs/M4-MODEL-EVAL-EVIDENCE.md` for the selected dogfood-derived fixture.
- `REQ-002`: run focused model-eval tests covering latency/tool/truncation-compatible records plus `refusal_flags` validation.
- `REQ-003`: inspect `MODEL_EVALUATION_MODEL_BACKED_SCENARIOS` and score output for expanded decision-eligibility coverage.
- `REQ-004`: inspect `docs/MODEL-EVALUATION.md` and bake-off evidence showing Ministral remains the baseline until repeated candidate evidence wins.
- `REQ-005`: run focused fixture/record tests, `git diff --check`, and the publication scan path in the milestone gate before integration.
- `REQ-006`: inspect updated model-evaluation documentation and M4 evidence notes for recommendation limits.
- `make check` before integration.
- Local model-eval dogfood only when a repeatable fixture exists and the configured endpoint is available.
- Full gate before promotion: `make milestone-gate`.

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

- `REQ-001` -> `plan-validation-command-grounding` fixture and `docs/M4-MODEL-EVAL-EVIDENCE.md`.
- `REQ-002` -> `refusal_flags`, existing latency/truncation/tool metrics, and validation tests.
- `REQ-003` -> required-scenario set and decision eligibility rule.
- `REQ-004` -> baseline comparison notes in `docs/MODEL-EVALUATION.md`.
- `REQ-005` -> bounded model-eval records and publication scan.
- `REQ-006` -> `docs/MODEL-EVALUATION.md` and `docs/M4-MODEL-EVAL-EVIDENCE.md`.


## Validation Evidence

- Added `plan-validation-command-grounding` from the observed Qwen failure where a candidate recommended unavailable `pytest` validation in a stdlib-only fixture.
- Existing `plan-repo-change` now also rejects `pytest` so models cannot pass by listing both correct and unavailable validation paths.
- Added `refusal_flags` as a separately recorded numeric model-eval metric and kept hallucination flags reserved for unsupported edit/test/line-reference claims.
- Focused model-eval tests passed: 13 passed, 159 deselected.
- Ruff, strict mypy, `make check`, and full pytest passed during active implementation.
- `make milestone-gate` passed before completion: Ruff, pytest, Harness Score L4, validation/publication scan, and VSIX inspection.
- Focused dogfood of `plan-validation-command-grounding` on Ministral passed with score 100.0, 3 tool calls, no refusals, no hallucinations, and no changed paths; source tree was dirty, so it is not final decision-eligible evidence.
