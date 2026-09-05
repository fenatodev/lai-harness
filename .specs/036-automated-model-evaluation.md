# Spec: Automated model evaluation

## Metadata
- Mode: `full`
- Status: `complete`
- Target: `0.4.0-beta.20`

## Goal
Turn the existing model-evaluation rubric into a repeatable local runner that measures the already-loaded model on fixed LAI coding-agent fixtures without changing the configured default model.

## Context and Constraints
- The first manual bake-off compared Ministral 3 8B Q4_K_M with Qwen2.5-Coder-7B-Instruct Q4_K_M.
- Model evaluation may contact the configured authenticated endpoint only through `lai model run`.
- Runtime remains Python standard-library-only.
- Live evaluation results belong under LAI data state, not public source by default.

## Requirements
### REQ-001 — Reproducible fixtures
Create isolated temporary Git repositories for plan, debug, implement, review, and security scenarios from a versioned fixture definition.

### REQ-002 — Objective validation
Each scenario has machine-checkable exit, mutation, evidence, and independent-validation invariants.
### REQ-003 — Claim verification
Detect objective claim/evidence mismatches including claimed edits without a diff, claimed passing validation when the independent validator fails, and impossible line references.

### REQ-004 — Measurement capture
Capture latency, prompt/completion tokens, tool calls, truncation retries, policy blocks, hallucination flags, and bounded model/server/hardware metadata.

### REQ-005 — Durable local results
Write versioned JSONL plus JSON summaries under `$LAI_DATA_DIR/model-eval` and synchronize the canonical fixture for installed LAI copies.

### REQ-006 — Comparison
Allow `lai model score` to combine one or more safe result files, including `latest`, while preserving the existing scoring rubric.

### REQ-007 — Repeated evidence
Support bounded repetitions and mark a model result decision-eligible only after all model-backed scenarios have at least two samples.

### REQ-008 — Provenance and invariance
Record executable/fixture hashes and available Git provenance; preserve the source checkout HEAD/status across live evaluations.

### REQ-009 — Safety boundary
Never download, start, stop, switch, fine-tune, automatically select, tag, push, publish, or expand remote shell authority from model evaluation.
## Acceptance Criteria
- `lai model run` evaluates only the currently loaded authenticated endpoint model.
- Fixture repositories are disposable and the source checkout remains invariant.
- False edit/test claims and impossible line evidence raise hallucination flags.
- Results persist outside the public repository with enough provenance to compare later runs.
- Repeated runs can be scored across multiple files/models; a single sample is never decision-eligible.
- `lai model plan`, `sample`, and `score` remain deterministic/model-free.
- Full project validation and publication gates pass.

## Validation
- `REQ-001/002/003`: focused fixture, claim-verification, and false-implementation regressions.
- `REQ-004/005/006/007/008`: focused persistence, repeat-bound, install-smoke, and multi-file scoring regressions plus live Ministral dogfood.
- `REQ-009`: deterministic command regressions, source-tree invariance checks, and full publication gates.
- Full gates: `make lint`, `make typecheck`, `make check`, `make test-dev`, `make test`, `make harness-score-gate`, `make validate`.

## Non-Goals
- Automatic model downloading or switching.
- Fine-tuning, LoRA/QLoRA, or weight updates.
- Automatic replacement of the default model.
- Generic self-modifying behavior.
- New remote shell authority.
## Traceability
- `REQ-001/002/003` -> `model-eval/fixtures-v1.json`, `src/local-agent`, `tests/test_local_agent.py`.
- `REQ-004/005/006/007/008` -> model-evaluation runner/scorer, `scripts/install-local.sh`, install smoke, model-eval regressions, `docs/MODEL-EVALUATION.md`.
- `REQ-009` -> CLI dispatch/safety boundaries, release/publication tests, `docs/MODEL-BAKEOFF-2026-09-05.md`.

## Validation Evidence
- Focused model-evaluation/install/release regressions: 14 passed before full gates; dedicated new-runner regressions: 11 passed.
- Full pytest: 225 passed + 72 subtests.
- Full unittest: 225 passed.
- Ruff, strict mypy, compile/static checks, and `git diff --check`: green.
- Harness maturity no-regression gate: L4, 100/108 (93%).
- Publication scan and VSIX inspection: green.
- Live Ministral dogfood exercised all five model-backed fixtures; the runner independently caught a repeated review miss, proving failures are not normalized away.
- Manual Ministral/Qwen bake-off remains preliminary evidence only; the default model was not changed.
