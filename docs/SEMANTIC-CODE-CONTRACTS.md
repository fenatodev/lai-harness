# semantic code contracts

`lai semantics` prints the semantic map that lai harness uses to describe its own codebase to small local models.

The contract is deliberately advisory. It helps the model choose likely files, but it does not replace `read`, `inspect`, `search`, or `git` evidence.

## command

```bash
lai semantics
lai semantic --json
```

The command is deterministic. It does not contact the model server, start a server, download a model, or inspect private files outside the repository.

## what the contract contains

Each subsystem declares:

- a stable subsystem id;
- the subsystem intent;
- canonical source and documentation paths;
- important entrypoints;
- domain terms that should trigger the subsystem during context ranking.

Examples of subsystem ids:

- `configuration`
- `policy-gateway`
- `tool-runtime`
- `context-intelligence`
- `spec-workflow`
- `model-evaluation`
- `observability-recovery`
- `extension-shell`
- `installation-publication`

## how context ranking uses it

When task terms match a subsystem, `lai context` can add a reason such as:

```text
semantic_contract:policy-gateway
```

That means the file is likely relevant by declared domain meaning. It does not mean the file was read. The model must still inspect the file before relying on implementation details.

## why this helps small models

Small local models have less room for long prompts and broad repository scans. Semantic contracts give them compact domain hints before they decide what to inspect.

This reduces:

- irrelevant file reads;
- broad search loops;
- accidental edits in the wrong subsystem;
- hallucinated architecture claims.

## maintenance rule

When a subsystem is renamed, moved, split, or given new public behavior, update the contract and tests in the same change.
