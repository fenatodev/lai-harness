# M4 model-eval evidence expansion

Status: complete implementation evidence for `.specs/057-model-eval-evidence-expansion.md`.

## Selected dogfood failure

The first Qwen candidate bake-off produced a concrete planning failure: in a stdlib-only synthetic repository, the model proposed `pytest` even though the fixture exposed `unittest` and no third-party runner. That is small, repeatable, and directly relevant to local-model selection because it tests whether a candidate grounds validation advice in repository evidence instead of defaulting to familiar tooling.

## Fixture change

M4 adds `plan-validation-command-grounding`, a read-only planning fixture with:

- explicit stdlib-only `AGENTS.md` guidance;
- a `test_string_utils.py` unittest test file;
- required output evidence for `unittest` and the test file;
- forbidden output patterns for `pytest` and `pip install`.

The existing `plan-repo-change` fixture also rejects `pytest`, closing the loophole where a model could mention both a correct command and an unavailable one.

## Measurement change

The runner now records `refusal_flags` separately from `hallucination_flags`. Refusals and generic AI disclaimers are quality signals, but they are not the same failure class as claiming an edit happened without a diff or citing impossible line numbers.

## Decision impact

The required model-backed scenario set expands from five to six. Previous repeated Ministral records remain useful historical baseline evidence, but they are not fresh decision-eligible evidence for the expanded suite until the new fixture receives repeated coverage.

The default model remains unchanged. Qwen or any other candidate still needs repeated coverage across the expanded required set, better correctness/validation behavior, no worse policy obedience, and acceptable latency before it can displace Ministral.

## Focused dogfood

A focused in-progress run exercised only `plan-validation-command-grounding` against the currently loaded Ministral endpoint:

- result: `pass` / `pass`;
- score: `100.0`;
- tool calls: `3`;
- truncation retries: `0`;
- policy blocks: `0`;
- hallucination flags: `0`;
- refusal flags: `0`;
- changed paths: none;
- saved result: `$LAI_DATA_DIR/model-eval/20260908T054108Z-25fec161-mistralai-Ministral-3-8B-Instruct-2512-GGUF-Q4_K_M.jsonl`.

The source tree was intentionally dirty during this run because M4 was still being implemented, so the run is focused fixture evidence, not final decision-eligible model-selection evidence.

## Final validation

The M4 implementation passed the local milestone gate before completion:

- `make check` passed.
- Focused model-eval regression tests passed: 13 passed, 159 deselected.
- Full pytest passed: 325 passed, 144 subtests passed.
- `make milestone-gate` passed: Ruff, pytest, Harness Score L4 at 103/108, `validate.sh`, publication scan, package generation, and VSIX inspection.

No default model, release tag, GitHub push, MCP execution permission, or browser/action authority was changed.
