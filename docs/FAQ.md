# FAQ

## Is `lai harness` a hosted AI product?

No. It is a local-first developer harness. You provide the local model endpoint and run the CLI/control plane locally.

## Does it include a model?

No. It talks to an OpenAI-compatible local server that you configure separately.

## Can it write directly to my repository?

Local write modes can edit files under deterministic path and validation guards. Remote work-runs use safe workspaces and promotion. Source checkout writes through the control plane are disabled.

## Is the sandbox a complete security boundary?

No. The verified sandbox boundary applies to remote work-runs and selected fixtures. It improves containment, but the project does not claim to safely execute arbitrary hostile code in all contexts.

## Does it support browser automation?

Only a local `fixture_browser` contract is implemented. Real browser profiles, login, JS automation and public browsing are not enabled.

## Does MCP execute real tools?

Generic MCP `call-tool` remains denied. The implemented execution path is a fixture stdio adapter with a single bounded `write_artifact` tool.

## Can it push to GitHub or open PRs?

No real GitHub external action is enabled. The current external action adapter is fake and receipt-producing.

## Why are A10 and A11 not complete?

They intentionally remain experimental draft specs because trusted-host and computer-use boundaries require a separate risk decision and additional proof.

## Which docs should I trust first?

Use `README.md`, [docs/README.md](README.md), [Architecture](ARCHITECTURE.md), [Security model](SECURITY-MODEL.md), [Control plane](CONTROL-PLANE.md) and [Known limitations](KNOWN-LIMITATIONS.md). Historical planning docs are traceability records, not current capability claims.
