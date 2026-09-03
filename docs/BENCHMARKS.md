# Experimental benchmarks

These results document design feedback from one development setup. They are not standardized benchmarks, cross-model comparisons, or performance guarantees.

## Reference setup

- native Windows `llama.cpp` server accessed from WSL;
- Ministral 3 8B Instruct 2512 GGUF, Q4_K_M;
- context size 16,384;
- all GPU layers, flash attention, parallelism 1;
- K/V caches using q8_0;
- Jinja chat template and OpenAI-compatible tool calling.

Exact CPU, GPU, RAM, llama.cpp build, thermal state, and prompt cache conditions were not captured consistently enough for a reproducible hardware score. Results are therefore retained as approximate development observations.

## Observed task latency

| Synthetic task | Approximate wall time |
| --- | ---: |
| Review | 8–10 s |
| Plan | 17 s |
| Debug | 22 s |
| Implement with sanity | 32 s |

## Batch architecture fixture

One implementation fixture evolved from approximately 14 API calls and 15 tool calls at about 40 seconds to approximately 5 API calls and 3 tool calls at about 32 seconds after batch inspection/patching and sanity integration.

The important observation was not a universal speedup percentage. On this local 8B setup, prefill, repeated schemas, and inference round-trips often mattered more than final-answer generation. Reducing rounds could improve usability even when an extra sanity pass added work.

## Earlier harness comparison

Approximate exploratory measurements included:

| Path | Prompt tokens | Time |
| --- | ---: | ---: |
| OpenCode without tools | 2,415 | 27.5 s |
| OpenCode local-dev profile | 5,822 | 121 s |

A compact raw call was substantially faster in the same experiment. These observations motivated a custom constrained harness; they do not characterize current OpenCode releases or other hardware.

## Better future methodology

Future reports should publish synthetic fixtures, warm/cold-cache state, exact hardware and software versions, quantization, prompt/completion tokens, API calls, tool calls, schema count, inference duration, and multiple-run distributions.
