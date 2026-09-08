# lai harness project presentation

## One-line description

`lai harness` is a local-first, auditable coding harness that gives small OpenAI-compatible local models deterministic structure, policy gates, safe workspaces and validation records.

## Why it exists

Local coding models need help with context selection, tool discipline and safety boundaries. The harness supplies deterministic repository metadata, bounded tools, explicit validation and review/promotion workflows so useful work can happen without treating model output as authority.

## What is implemented

- CLI wrapper and model-backed coding modes.
- Deterministic context map, changes, checks, symbols and Python code graph.
- Authenticated loopback control plane and Gateway/local-chat contract.
- Safe workspaces and verified sandbox work-runs.
- Metadata-only trajectory, audit, metrics and budget records.
- Authority intents, fake credential refs, governed egress and fake external-action receipts.
- Fixture browser, fixture MCP and bounded delegate/fork contracts.
- Distribution diagnostics and risk-proportional validation matrix.

## What is not implemented

- Real cloud service or hosted control plane.
- Real credential use.
- Real GitHub push/PR/merge/tag/release automation.
- Real browser profile/login automation.
- Generic MCP tool execution.
- Trusted-host or computer-use A10/A11 capabilities.

## Architecture narrative

1. The developer invokes `lai` or a companion Gateway calls the loopback control plane.
2. The harness resolves config, mode, repository status and advisory context.
3. The model receives bounded prompts and tools.
4. Every tool crosses deterministic policy and budget gates.
5. Work-runs happen in safe workspaces and the verified sandbox.
6. Review and promotion require exact hashes and validation evidence.
7. Records remain metadata-only on public surfaces.

## Demonstration path

```bash
./src/lai --help
./src/lai readiness
./src/lai context map
./src/lai validation matrix
./src/lai gateway-contract --json
```

For a control-plane demonstration:

```bash
lai control-token init
lai serve --bind 127.0.0.1 --port 8765
lai chat-bootstrap --control-url http://127.0.0.1:8765 --json
```

## Maintainer message

The project is strongest when it remains narrow: local-first, auditable, deterministic where possible and honest about fixture-only versus real external capabilities.
