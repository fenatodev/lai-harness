# Development harness

This repository uses a separate development harness around the `lai harness` product runtime. Its job is to catch risky or low-quality agent actions before they become repository changes, while keeping final CI as the authority.

## Maturity target

The repository pins `harness-score` 1.6.3 for reproducible measurements.

```bash
make harness-score
make harness-score-gate
```

`make harness-score-gate` requires L4. Beta.9 reached L4 Self-correcting at 93/108 (86%), up from the beta.8 L3 baseline of 76/108 (70%). Beta.16 raises the measured maturity to 100/108 (93%) by adding real reproducible-sensor and type-checking capabilities.

The project does not add subagents, MCP configuration, type checking, or dependency metadata solely to gain score points. Beta.16 adds the latter two because they now enforce reproducible CI sensors and a strict typed guardrail boundary. Subagents and MCP remain deferred until real delegation and governed broker boundaries exist.

## Reproducible static sensors

`requirements-dev.in` is the small human-maintained sensor manifest. `requirements.txt` is generated from it with exact direct/transitive versions and is the canonical CI install input. The product runtime installer does not consume either file.

`mypy.ini` starts with `strict = True` on the two Python guardrail hooks. `make typecheck` and `make validate` enforce that boundary, while CI runs the same check on Python 3.11 and 3.12. The scope should expand as runtime subsystems move out of the extensionless `src/local-agent` monolith into importable modules.

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
## GitHub Actions supply-chain policy

Official GitHub Actions used by CI are pinned to reviewed full commit SHAs with the upstream release version recorded in an inline comment. Do not replace them with floating `@vN` references. `.github/dependabot.yml` may propose GitHub Actions pin updates, but those updates still pass the normal PR and protected-main validation path.

Publication setup-node uses Node.js 24 explicitly and disables package-manager caching when no npm dependency cache is required.
