---
name: verify-change
description: Use when a code or harness change is ready for deterministic verification before commit, PR, or release work.
---

# Verify change

1. Inspect `git status --short` and `git diff --check` before claiming completion.
2. Run the narrowest focused tests that cover the changed behavior.
3. Run `make lint` and `make check` after focused tests pass.
4. For runtime or release-critical changes, run both `make test-dev` and `make test`.
5. Before release work, run `make validate` and inspect `lai release-check --json`.
6. If agent-harness files changed, run `npx --yes harness-score@1.6.3 . --min-level 4`.
7. Report failures as evidence; never weaken a gate merely to make verification green.
