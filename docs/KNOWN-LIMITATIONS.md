# Known limitations

This document lists current limitations after A12. It is deliberately conservative.

## Platform and runtime

- Linux/WSL2 is the first-class target. Native Windows desktop automation is not implemented.
- Python 3.11+ is required because the runtime uses stdlib `tomllib`.
- A local OpenAI-compatible model server must be provided separately.
- Docker is required for verified work-runs and sandboxed fixtures.

## Autonomy

- A10 trusted-host and A11 computer-use are fixture-only experimental contracts, not real host, app, or personal desktop automation.
- The harness does not provide arbitrary host shell execution through the remote control profile.
- The sandbox executor does not run if the required digest-pinned image is missing; it does not pull automatically.
- Local CLI use is not a complete OS security sandbox.

## External systems

- Real credentials are disabled; the credential broker uses a fake adapter in current tests.
- Real GitHub push, PR, merge, tag, release and remote settings mutation are not enabled.
- Browser support is `fixture_browser` only. No real Chromium, personal profile, login or public browser automation is shipped.
- MCP execution is limited to `fixture_stdio` `write_artifact`; generic MCP `call-tool` remains denied.
- Web evidence is untrusted and read-only.

## Intelligence and routing

- Code graph support is Python AST only. JS/TS are represented by existing symbol/pattern metadata, not a full graph.
- Model capability profiles do not switch models automatically.
- Skills are diagnostics/instructions only and cannot grant tools or authority.
- Delegate waves are fixture-only and bounded; no unbounded swarm is implemented.

## Documentation and publication

- Historical docs remain for traceability and may describe earlier plans or releases. Use [docs/README.md](README.md) to find current canonical documents.
- The local A0-A12 package is validated, but GitHub publication still requires explicit maintainer commit/push/release decisions.
