# Spec: semantic code contracts

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Add explicit semantic code contracts so small local models can understand the main lai harness subsystems, canonical files, domain terms, and entrypoints with less guesswork and fewer broad searches.

## Requirements

### REQ-001

The runtime must expose a deterministic `lai semantics` command that prints the product's semantic code contract without contacting the model server.

### REQ-002

The semantic contract must describe subsystem intent, canonical files, entrypoints, domain terms, and rules that distinguish advisory metadata from inspected evidence.

### REQ-003

Context ranking must use semantic contract matches as an additional advisory signal while keeping ranked candidates metadata-only.

### REQ-004

The `lai`, `semantic`, and `semantics` command paths must work through the wrapper while preserving existing commands and compatibility identifiers.

### REQ-005

The version must advance to `0.4.0-alpha.15` across CLI and VS Code extension metadata.

## Acceptance Criteria

- `lai semantics` reports `# lai code semantics` and includes subsystem ids such as `policy-gateway` and `context-intelligence`.
- `lai semantic --json` emits parseable JSON with product, version, rules, and subsystem metadata.
- `lai context` can rank files through `semantic_contract:<subsystem>` reasons when task terms match a subsystem.
- Deterministic commands do not require a running model server.
- Tests cover the semantics command, context semantic signal, wrapper smoke, and version metadata.

## Validation

- `REQ-001`: run deterministic semantics CLI tests without a model server.
- `REQ-002`: inspect `SEMANTIC_CODE_CONTRACT` and parse `lai semantic --json`.
- `REQ-003`: run context ranking tests that expect `semantic_contract:policy-gateway`.
- `REQ-004`: run install smoke tests for the wrapper command.
- `REQ-005`: run version tests and parse `vscode-extension/package.json`.

## Context and Constraints

Semantic contracts are a navigation aid. They must not become hidden authority. The model must still inspect files before using code as evidence or editing it.

## Non-Goals

- Do not split `src/local-agent` into modules in this milestone.
- Do not change policy decisions, tool behavior, or approval rules.
- Do not rename compatibility identifiers.
- Do not make context candidates count as inspected evidence.

## Implementation Notes

Keep the contract deterministic, small, and directly tied to current source paths. Prefer stable subsystem ids over prose-heavy comments. Context ranking should add one clear reason string per matched subsystem so audit output remains readable.

## Traceability

- `REQ-001` -> `render_semantic_code_contract` and CLI tests.
- `REQ-002` -> `SEMANTIC_CODE_CONTRACT` and JSON semantics tests.
- `REQ-003` -> `context_semantic_references` and ranking tests.
- `REQ-004` -> `src/lai` wrapper changes and install smoke tests.
- `REQ-005` -> version tests and package metadata checks.
