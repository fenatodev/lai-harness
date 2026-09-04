# Design decisions

## Custom harness over a general-purpose default

Early OpenCode experiments worked but introduced prompt and schema overhead that was disproportionate for the tested 8B model. LAI chose a small standard-library harness to control every prompt, tool, and round. This trades ecosystem breadth for inspectability and lower overhead.

## Batch inspection

Sequential read→infer cycles repeatedly paid prefill and tool-call costs. `inspect` reads several already-known files together and, in debug mode, follows bounded local JavaScript/TypeScript dependencies. The tradeoff is a hard cap that can omit wider context.

## Deterministic context ranking

Small models should not spend several inference rounds merely discovering likely files. Before selected modes call the model, LAI ranks a bounded repository inventory using explainable signals from the task, live Git changes, verified workspace state, active-spec references, manifests, and bounded text sampling. Only path/score/reason metadata is injected. This reduces discovery overhead without introducing embeddings, a vector database, or another model-facing tool.

## Transactional batch patch

`patch` validates exact unique replacements across all targets before writing. This reduces rounds and prevents a predictable stale second replacement from leaving a partial logical batch. It is not an OS-level transaction; an I/O failure during writes can still leave partial results.

## Dedicated read-only Git tool

Review modes need diffs without mutation. The Git schema exposes only status and diff operations. Shell access is a separate, weaker trust boundary and is never described as read-only.

## Evidence gates

Small models produced plausible but unsupported review findings. Review and security skills require repository evidence, while a second compact classifier and deterministic filters remove common false positives. The gate can still miss true findings or retain incorrect ones.

## Post-patch sanity

A fixture introduced `throw newError(...)`; tests passed because that branch was not executed. LAI added deterministic syntax and added-line analysis, including this regression class, followed by a very small diff-only model check. Sanity complements rather than replaces project validation.

## Metrics and audit

Optimization without round/token timing was guesswork, and edits without provenance were difficult to reconstruct. JSONL keeps records append-friendly and easy to inspect. The tradeoff is sensitive local metadata requiring retention discipline.

## Model-configurable, model-informed

The public extraction makes the model identifier configurable while retaining the tested Ministral default. It avoids claiming universal model compatibility: tool-call formatting and instruction following still depend on the selected server, template, and model.
