# Development harness

This repository uses a separate development harness around the `lai harness` product runtime. Its job is to catch risky or low-quality agent actions before they become repository changes, while keeping final CI as the authority.

## Maturity target

The repository pins `harness-score` 1.6.3 for reproducible measurements.

```bash
make harness-score
make harness-score-gate
```

`make harness-score-gate` requires L4. During the beta.9 cut the repository measures L4 Self-correcting at 93/108 (86%), up from the beta.8 L3 baseline of 76/108 (70%).

The project does not add subagents, MCP configuration, a type checker, or dependency metadata solely to gain score points. Those mechanisms should be added only when they solve a real reliability or product problem.

## Policy-backed shell gate

`.cursor/hooks/guard_shell.py` is a `beforeShellExecution` gate. It does not maintain an independent destructive-command list. Instead it sends the proposed shell command to:

```bash
lai policy-check --tool bash --command 'git status --short' --json
```

`lai policy-check` reuses the runtime `evaluate_tool_policy` boundary and always reports `executed: false`.

Hook mapping is deterministic:

- `ALLOW` -> allow;
- `ASK` -> require explicit user review/action;
- `DENY` -> block;
- malformed input, unavailable policy evidence, or invalid output -> ask/fail closed.

The beta.9 policy explicitly denies force push, hard reset, npm publication, recursive forced deletion, privilege escalation, selected destructive Docker operations, and destructive database operations. Ordinary Git mutations remain `ASK` rather than executing automatically.

## Feedback hook

`.cursor/hooks/feedback_check.py` runs after file edits. It is repository-confined, never installs dependencies, and is intentionally best-effort/non-blocking.

Depending on the edited file it can run narrow checks such as Python compilation/Ruff, `node --check`, JSON parsing, or `bash -n`. A hook diagnostic is early feedback, not proof of correctness; focused tests and CI remain required.

## Explicit verification workflow

`.agents/workflows/verify-change.md` records the intentional verification sequence: focused tests first, then lint/static checks, full suites for runtime/release-critical work, publication validation before release, and the L4 gate when harness files change.

## CI ratchet

`.github/workflows/harness-score.yml` is deliberately separate from the product CI workflow. It uses a pinned Harness Score action revision and requires `min-level: 4`.

For beta.9 and later, protected `main` should require all four checks:

- `Python 3.11`
- `Python 3.12`
- `Publication gates`
- `Harness Score L4`

`lai release-governance --remote` verifies the same required-check set so repository policy and release verification cannot silently diverge.
