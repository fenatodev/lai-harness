# Model Evaluation

LAI Harness keeps the current model until a replacement wins in repeatable local tests. The benchmark harness is deterministic and does not download, start, or contact a model server.

Use it to compare small local coding models on the actual LAI workflow instead of switching defaults based on general benchmarks.

## Commands

```bash
lai model plan
lai model plan --json
lai model sample > model-eval/results.jsonl
lai model score model-eval/results.jsonl
```

`lai models` is accepted as the same command group. Result paths are repository-relative and paths outside the repository fail closed.

## Scenarios

The built-in plan covers:

- planning a repository change without editing;
- debugging with reproduction and source evidence;
- implementing a small validated diff;
- reviewing only supported findings;
- inspecting security-sensitive changes defensively;
- ranking likely context files without calling the model.

## Result format

Each result is one JSON object per line. Required fields are:

- `model`
- `scenario`
- `outcome`: `pass`, `partial`, `fail`, or `not_run`
- `validation`: `pass`, `fail`, or `not_run`

Optional numeric fields default to zero when absent:

- `latency_ms`
- `prompt_tokens`
- `completion_tokens`
- `tool_calls`
- `truncation_retries`
- `policy_blocks`
- `hallucination_flags`

Use `notes` for short human observations. Do not put secrets, API keys, private prompts, or wallet data in benchmark records.

## Decision rule

A model should replace the default only when it clearly improves correctness and validation while keeping policy obedience and latency acceptable. Close scores, too few records, or worse safety behavior mean the current default stays.

## Out of scope

This milestone does not download models, redistribute weights, change licenses, select a new default, add provider abstraction, or run long automatic benchmarks. It only adds the local measurement layer.
