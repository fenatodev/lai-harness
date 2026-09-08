# Model capabilities

Model capability profiles are deterministic summaries of model-evaluation JSONL records. They are evidence descriptors, not an automatic router.

## Current behavior

`lai model profile <results.jsonl|latest> [--json]` reports:

- schema version;
- model and evidence metadata;
- required scenario coverage;
- dimensions such as planning, coding, debug, tools, context, patch, latency, refusal, truncation, hallucination and validation;
- explicit `unknown` for missing evidence;
- conservative recommendation.

The profile never downloads a model, switches the default model, enables cloud fallback, or starts an automatic router.

## Evidence requirements

A profile can become decision-eligible only when the required model-backed scenarios have enough repeated samples. Even then, the current implementation preserves manual selection and keeps auto-switch disabled.

## Related docs

- [Model evaluation](MODEL-EVALUATION.md)
- [Configuration](CONFIGURATION.md)
- [Known limitations](KNOWN-LIMITATIONS.md)
