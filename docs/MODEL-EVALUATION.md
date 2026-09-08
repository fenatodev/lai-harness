# Model Evaluation

lai harness keeps the current model until a replacement wins in repeatable local tests on the actual LAI workflow.

The model-evaluation surface has two boundaries:

- `plan`, `sample`, and `score` are deterministic and do not contact a model server;
- `run` evaluates only the model already loaded on the configured authenticated endpoint.

The runner never downloads, starts, stops, switches, or selects a default model.

## Commands

```bash
lai model plan
lai model plan --json
lai model sample
lai model run
lai model run --scenario implement-small-diff
lai model run --repeat 2
lai model run --repeat 2 --json
lai model score latest
lai model score first.jsonl second.jsonl
```

`lai models` is accepted as the same command group.
## Automated fixtures

Versioned fixtures live in `model-eval/fixtures-v1.json`. A local installation receives the same file under `$LAI_DATA_DIR/model-eval/fixtures-v1.json`.

The model-backed runner covers:

- `plan-repo-change` — inspect and plan without editing;
- `plan-validation-command-grounding` — recommend repository-supported validation without inventing unavailable tools;
- `debug-repro` — reproduce a failing unittest and identify root cause;
- `implement-small-diff` — make one bounded fix and pass independent validation;
- `review-supported-findings` — review a pre-existing diff without mutating it;
- `security-defensive` — report a grounded defensive security finding.

Each invocation creates disposable Git repositories on `test/model-eval`. Fixture repositories are removed after the run.

The source repository HEAD and exact Git status are captured before execution and must be identical afterwards. A mismatch fails the evaluation run.

## Objective evidence

The runner reads LAI's isolated metrics/audit streams for each fixture instead of estimating activity from prose.

It captures latency, prompt/completion tokens, tool calls, truncation retries, policy blocks, refusal flags, model alias, model file type, context size, CPU/platform profile, harness commit, and fixture SHA-256.
Machine checks currently flag at least:

- claimed implementation when the Git diff did not change;
- claimed successful validation when the independent validator failed;
- cited line numbers beyond the maximum line count of the synthetic fixture;
- forbidden validation/tool recommendations such as `pytest` in stdlib-only fixtures;
- refusal/disclaimer patterns separately from hallucination flags.

A bounded response excerpt and SHA-256 are retained with each synthetic-fixture record for later diagnosis. These checks do not attempt to solve every form of hallucination.

## Result storage

Automated results are private local runtime evidence by default:

```text
$LAI_DATA_DIR/model-eval/<run>-<model>.jsonl
$LAI_DATA_DIR/model-eval/<run>-<model>.summary.json
```

`lai model score` accepts result files inside the current repository or the configured model-evaluation data directory. `latest` resolves the newest local JSONL result.

Manual `sample` output remains available when human-scored scenarios are useful.

## Decision rule

A single run is diagnostic evidence, not a model-selection decision.

`lai model run` accepts `--repeat 1..5`. A run is marked `decision_eligible` only when all required model-backed scenarios are present and each has at least two samples.
A candidate should replace the default only when repeated results clearly improve correctness and independent validation without worse policy obedience or hallucination behavior, while keeping latency acceptable.

Close scores, incomplete scenario coverage, too few samples, or worse safety behavior mean the current default stays.

## Current baseline

The configured baseline remains:

```text
mistralai/Ministral-3-8B-Instruct-2512-GGUF:Q4_K_M
```

The first Qwen bake-off is recorded in [Model bake-off — 2026-09-05](MODEL-BAKEOFF-2026-09-05.md). It is historical evidence, not a universal claim about Qwen performance.

The pre-M4 repeated baseline evidence contains 10 model-backed records across the original five required scenarios, with at least two samples per scenario. Aggregate score was **90.8/100** under that fixture set. `plan`, `debug`, `implement`, and `security` passed their repeated samples; `review-supported-findings` scored 55/100 twice with independent validation failure. That weakness remains visible and is not treated as a harness success.

M4 expands the required fixture set with `plan-validation-command-grounding`, based on the observed Qwen failure where the candidate proposed unavailable `pytest` validation in a stdlib-only repository. Until the expanded suite is rerun with repeated coverage, prior baseline records are historical support for keeping Ministral, not fresh decision-eligible evidence under the new fixture set.

This evidence supports keeping Ministral as the stable default for now; it does not prove Ministral is universally better than other models. A replacement still requires a new candidate to win the same repeated, validated workflow.

## Out of scope

This milestone does not:

- download or redistribute models;
- change model licenses;
- switch the running model;
- replace the configured default automatically;
- fine-tune weights or run LoRA/QLoRA;
- add provider abstraction;
- authorize a model to modify the harness outside normal safe-workspace, validation, promotion, PR, and CI boundaries.
