# Contributing

Contributions should preserve LAI's central constraint: useful local agent behavior with small prompts, few tool schemas, and few inference rounds.

1. Open an issue describing the observable problem or measured opportunity.
2. Use only synthetic fixtures; never submit private repositories, prompts, logs, keys, or customer data.
3. Keep patches focused and include a regression test when behavior changes.
4. Run `python3 -m unittest discover -s tests -v`, Python compilation, Node syntax checking, shell syntax checking, and `git diff --check`.
5. Explain performance claims with hardware, model, fixture, and methodology.

Security vulnerabilities should follow [SECURITY.md](SECURITY.md), not a public issue.
