# Testing and validation

`lai harness` uses risk-proportional validation. The goal is to run enough evidence for the affected boundary without repeating equivalent expensive gates after every small edit.

## Matrix

```bash
lai validation matrix
lai validation matrix --json
```

The matrix is metadata-only. It does not execute checks, mutate remote settings or weaken existing gates.

Required check IDs currently include:

- `static.syntax`
- `lint.ruff`
- `runtime.pytest`
- `runtime.unittest`
- `typing.mypy`
- `harness.score`
- `publication.scan`
- `package.vsix`
- `install.smoke`

## Common commands

| Command | Purpose |
| --- | --- |
| `make check` | Static/syntax checks and `git diff --check`. |
| `make lint` | Ruff over runtime, tests and hooks. |
| `make test` | Dependency-free unittest suite. |
| `make test-dev` | Pytest developer suite. |
| `make typecheck` | Strict mypy ratchet over extracted modules/hooks. |
| `make validate` | Publication/package gate, including unittest, typecheck, static checks, publication scan and VSIX inspection. |
| `make milestone-gate` | Full local milestone/release freeze gate. |

## Risk profiles

- Docs/config: focused inspection and `make check`.
- Runtime code: focused regression, `make check`, then broader suite when coherent.
- Control-plane/security: focused adversarial tests, boundary tests and broad suite.
- Distribution/release: install/package smoke, broad suite, `test-dev`, milestone gate.
- Milestone freeze: `make milestone-gate` once for the final coherent state.

## Stop rules

Do not remove a retained coverage class to save time. Do not close a milestone without `make milestone-gate`. Do not mutate remote required-check settings from local validation commands. After a real failure, fix the cause and rerun the failing boundary plus final gate.
