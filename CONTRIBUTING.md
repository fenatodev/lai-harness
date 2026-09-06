# Contributing

Contributions should preserve LAI's central constraint: useful local agent behavior with small prompts, few tool schemas, and few inference rounds.

1. Open an issue describing the observable problem or measured opportunity.
2. Use only synthetic fixtures; never submit private repositories, prompts, logs, keys, or customer data.
3. Keep patches focused and include a regression test when behavior changes.
4. Install development sensors from the generated `requirements.txt`, then run `make typecheck`, `make lint`, `make check`, `make test-dev`, `make test`, and `make validate`. The runtime itself remains standard-library-only.
5. When changing development sensors, edit `requirements-dev.in` and regenerate `requirements.txt` with `uv pip compile requirements-dev.in --python-version 3.11 --output-file requirements.txt`; do not hand-edit the generated lock.
6. Explain performance claims with hardware, model, fixture, and methodology.

## Development cadence

Small changes should still be isolated, specified when needed, tested, and committed independently, but they do not require an individual public release. Related stabilization work may accumulate on a dedicated milestone branch while the published version remains unchanged. Bump release metadata and open the protected-main publication flow only when the milestone has a coherent scope, full regression evidence, and release-quality dogfood results.


Security vulnerabilities should follow [SECURITY.md](SECURITY.md), not a public issue.
