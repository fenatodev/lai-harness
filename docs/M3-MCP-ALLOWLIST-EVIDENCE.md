# M3 MCP allowlist evidence

## Baseline captured

The current Harness MCP foundation was checked before writing the design.

Observed local policy:

- MCP status: `ALLOW`, `executed=false`.
- MCP list-tools: `ALLOW`, `executed=false`.
- MCP call-tool: `DENY`, `executed=false`.
- MCP execution flag: false.

## External evidence reviewed

The design was checked against the MCP 2026-07-28 public specification and release notes.

Relevant points incorporated:

- MCP tools can be model-invoked, so human-visible policy and denial remain necessary.
- Tool listing can vary by authorization and should be deterministic.
- HTTP authorization uses bearer headers, not query-string tokens.
- Security guidance emphasizes audience-bound tokens and no token passthrough.
- The 2026-07-28 release added routing/caching changes and continued authorization hardening.

## Design result

M3 defines one future candidate operation class: `repo_public_text_read`.

It remains design-only. The Harness still denies MCP `call-tool`.

## Validation target

M3 is complete when:

- spec 056 is complete;
- design sections cover REQ-001 through REQ-006;
- publication scan passes;
- quality sensor passes;
- focused MCP foundation tests pass;
- `lai mcp policy-check --operation call-tool` still returns `DENY` and `executed=false`.
