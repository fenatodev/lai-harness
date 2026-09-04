# Roadmap

## Near term

- Extend semantic code contracts as subsystems split out of `src/local-agent`.
- Polish run-history detail views before broader tool-loop/session UX work.
- Extend the model-evaluation harness with automated run capture and hardware profiles.
- Harden the `ALLOW` / `ASK` / `DENY` policy with structured commands or a stronger execution boundary.
- Add configuration validation and a non-WSL server workflow.
- Expand end-to-end fixtures for every mode and guard.
- Package and test the VS Code extension reproducibly.
- Add JSON schemas and configurable retention for state, metrics, and audit events.

## Later

- Support multiple OpenAI-compatible local providers without provider-specific prompts.
- Add interactive approval UI and scoped approval grants for `ASK` operations.
- Provide an optional containerized/disposable executor.
- Use model-evaluation data to decide whether Qwen Coder or another <=8 GB model should replace the current baseline.
- Explore signed releases and provenance attestations.

Roadmap items are intentions, not commitments. Model redistribution and automatic downloading are deliberately out of scope.
