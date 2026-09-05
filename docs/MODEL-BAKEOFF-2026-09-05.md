# Model bake-off — 2026-09-05

Status: preliminary local evidence. This is not a universal model ranking.

## Purpose

The first LAI bake-off tested whether a coding-specialized model that fits the development machine should replace the existing Ministral baseline.

Models:

- baseline: `mistralai/Ministral-3-8B-Instruct-2512-GGUF:Q4_K_M`;
- candidate: `Qwen/Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M`.

The Qwen GGUF is published by the Qwen organization under Apache-2.0. Its official Q4_K_M file is 4.68 GB with SHA-256 `509287f78cb4d4cf6b3843734733b914b2c158e43e22a7f4bf5e963800894d3c`.

Reference: https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF

## Local setup

- Ryzen 7 third-generation development machine;
- 24 GB system RAM;
- Radeon RX 5500 XT with 8 GB VRAM;
- Windows-hosted llama.cpp accessed from WSL;
Server parameters were held constant where supported:

- context: 16,384;
- GPU layers: all (`-1`);
- parallel slots: 1;
- flash attention: on;
- K/V cache: q8_0;
- authenticated OpenAI-compatible endpoint;
- native model chat template/tool support from llama.cpp.

The Qwen model was loaded through the official llama.cpp/Hugging Face `-hf ...:Q4_K_M` path. After the comparison the endpoint was restored to Ministral and verified with authenticated `/props` plus `lai doctor`.

## First manual five-scenario sample

| Scenario | Ministral | Qwen2.5-Coder-7B |
| --- | --- | --- |
| plan | pass | partial |
| debug | pass | fail |
| implement | pass | fail |
| review | pass | pass |
| security | pass | partial |
| LAI score | **100.0** | **56.6** |

This first sample was manually orchestrated using fixed disposable repositories and then encoded into the existing LAI scoring format.
## Observed Qwen failures

The candidate was competitive on simple read-only review work but less reliable in tool-driven workflows:

- plan: proposed `pytest` even though the synthetic repository exposed stdlib `unittest` and pytest was unavailable;
- debug: reached the overall 12-round limit without a final diagnosis;
- implement: claimed the file was changed and tests passed, while Git showed no diff and independent unittest validation still failed;
- review: correctly reported a division-by-zero risk;
- security: found the `shell=True` command-injection risk but cited “line 42” in a four-line file.

The tool-capability metadata exposed by llama.cpp reported tool and tool-call support for the Qwen chat template, so the result was not treated as simply “tools unsupported”.

## Why this is not enough to declare a winner forever

During beta.20 development the first fully automated one-sample Ministral run scored **90.6**, not 100.0: plan/debug/implement/security passed, while review returned no finding for the division-by-zero fixture.

A second isolated review run repeated that miss. This demonstrates model variance and validates the rule that one sample cannot select a default.

Beta.20 therefore requires repeated full scenario coverage before a run is marked decision-eligible.

## Current decision

Keep Ministral as the default for now. The Qwen candidate did not demonstrate sufficient operational reliability in the first sample.
