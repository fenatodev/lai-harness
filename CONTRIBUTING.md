# Contributing

Contributions should preserve the central constraint of `lai harness`: useful local coding assistance with compact context, deterministic boundaries, explicit validation and no hidden authority expansion.

## Before opening a change

1. Read [AGENTS.md](AGENTS.md), [docs/README.md](docs/README.md), [Architecture](docs/ARCHITECTURE.md), [Security model](docs/SECURITY-MODEL.md), and [Testing and validation](docs/TESTING-VALIDATION.md).
2. Use a dedicated branch.
3. Use synthetic fixtures only. Do not submit private repositories, prompts, logs, keys, model files, handoffs, audit records, customer data or proprietary source.
4. Decide whether the change needs a spec. Behavior, policy, control-plane, sandbox, credential, egress, MCP, browser, release or validation changes usually do.
5. Keep patches focused and include regression coverage for behavior changes.

## Local setup

```bash
git clone https://github.com/fenatodev/lai-harness.git
cd lai-harness
python3 ./src/local-agent --version
./src/lai readiness
```

Development sensors are separate from runtime installation. The runtime installer remains standard-library-only.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

When changing development sensors, edit `requirements-dev.in` and regenerate `requirements.txt` with the documented pinned workflow. Do not hand-edit generated locks.

## Validation

Use the cheapest trustworthy check for the affected boundary:

```bash
make check
make lint
make test
make test-dev
make typecheck
make validate
make milestone-gate
```

`lai validation matrix` explains which evidence class applies. Do not claim a narrow test proves broader behavior. Do not weaken tests to make faulty code pass.

## Specs

Specs live in `.specs/`. Exactly one spec may be `active`. Draft and complete specs are inactive. Specs never override repository rules, safety guards or release policy.

For spec-driven changes:

1. Activate one spec.
2. Implement the smallest coherent slice.
3. Run focused tests.
4. Update documentation when the public contract changes.
5. Mark the spec complete only after evidence is green.

## Pull requests

A good PR includes:

- clear problem statement;
- implementation summary;
- capability status: implemented, fixture-only, experimental, planned/deferred or out of scope;
- validation commands and results;
- security/trust-boundary notes;
- screenshots or diagrams only when they reflect real behavior;
- no secrets or private local state.

Security vulnerabilities should follow [SECURITY.md](SECURITY.md), not public issues.
