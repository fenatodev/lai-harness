# Spec: Model Evaluation Harness

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Add a deterministic model-evaluation layer so LAI Harness can compare small local coding models before changing the default model.

## Requirements

### REQ-001

LAI Harness must expose a deterministic model-evaluation command through the `lai` wrapper while preserving the existing `lai` command and runtime flow.

### REQ-002

The command must render a fixed benchmark plan with coding-agent scenarios that cover planning, debugging, implementation, review, security, and context ranking.

### REQ-003

The command must emit a JSONL sample schema suitable for recording manual or automated benchmark results.

### REQ-004

The command must score repo-relative JSONL result files deterministically without contacting or starting a model server.

### REQ-005

The scorer must reject malformed records, missing required fields, invalid enum values, negative numeric metrics, and paths outside the repository.

### REQ-006

Documentation must explain that model downloads, licensing, default-model changes, and automatic claims are out of scope for this milestone.

### REQ-007

Validation must cover CLI routing, deterministic output, sample records, scoring, and path-safety behavior.

## Acceptance Criteria

- `lai model plan` prints the benchmark plan.
- `lai model plan --json` prints machine-readable benchmark metadata.
- `lai model sample` prints JSONL records for all built-in scenarios.
- `lai model score <path>` scores a repo-relative JSONL file.
- `lai model score ../outside.jsonl` fails closed.
- `lai version` reports `LAI Harness 0.4.0-alpha.13`.
- Existing agent modes and deterministic commands continue to work.

## Validation

- `REQ-001`: wrapper and deterministic CLI tests.
- `REQ-002`: plan-output tests and documentation review.
- `REQ-003`: JSONL sample parsing tests.
- `REQ-004`: scorer tests with multiple model records.
- `REQ-005`: malformed/path-safety tests.
- `REQ-006`: documentation checks.
- `REQ-007`: `make check`, `pytest`, `unittest`, and `make validate`.

## Context and Constraints

The user wants to compare the current Ministral baseline against code-oriented models such as Qwen without destabilizing the working setup. This milestone deliberately creates measurement infrastructure first. It must not download models, change the default model, or require network access.

## Non-Goals

- Downloading GGUF files.
- Selecting a new default model.
- Running long live benchmarks automatically.
- Adding provider abstraction.
- Adding web search or sandbox execution.

## Implementation Notes

Keep the harness deterministic and standard-library only. Result files are JSONL so future automation can append one record per scenario and model. Scoring is heuristic by design and should be used as decision support, not as proof of model quality.

## Traceability

- `REQ-001` -> `src/lai`, `src/local-agent`, tests.
- `REQ-002` -> model-evaluation scenario constants and docs.
- `REQ-003` -> sample command and tests.
- `REQ-004` -> scorer functions and tests.
- `REQ-005` -> record normalization/path checks and tests.
- `REQ-006` -> `docs/MODEL-EVALUATION.md`, README, roadmap.
- `REQ-007` -> validation suite.
