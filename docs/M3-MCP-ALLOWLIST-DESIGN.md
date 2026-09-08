# M3 MCP allowlist design

## Purpose

M3 defines the first governed path from the current non-executing MCP foundation toward one future, narrow, read-only MCP operation class.

This is a design milestone. It does not enable MCP `call-tool`, does not start an MCP server, and does not execute any external tool.

## Current baseline

The current Harness MCP foundation supports:

- `lai mcp status`: read declared MCP configuration without starting servers.
- `lai mcp tools`: list declared server metadata without starting servers.
- `lai mcp policy-check`: classify an MCP operation without execution.

Observed baseline:

- `status` operation: `ALLOW`, `executed=false`.
- `list-tools` operation: `ALLOW`, `executed=false`.
- `call-tool` operation: `DENY`, `executed=false`.
- MCP tool execution remains disabled.

## External protocol evidence reviewed

The design was checked against the MCP 2026-07-28 public specification and release notes.

Relevant protocol constraints:

- MCP tools are designed so models can discover and invoke external capabilities, so human-visible control and denial must remain part of the host design.
- Tool lists may vary based on authorization and should have deterministic ordering for cacheability and stable model context.
- HTTP authorization requires bearer tokens in headers rather than query strings, with tokens scoped to the intended MCP server.
- The 2026-07-28 revision adds routing/caching changes and continues hardening authorization and security behavior.

## REQ-001: candidate operation class

The only candidate operation class for a later implementation milestone is:

`repo_public_text_read`

Definition:

- server is explicitly allowlisted by name;
- tool is explicitly allowlisted by name;
- operation is read-only;
- arguments identify one repository-relative file path;
- target file must be tracked by Git or explicitly listed in a repository-owned fixture;
- target file must be text-like and under an allowed documentation or source-test surface;
- output is bounded, redacted, metadata-tagged, and treated as untrusted evidence.

Initial candidate mapping:

| Field | Candidate value |
| --- | --- |
| Operation class | `repo_public_text_read` |
| Server | declared MCP server, exact name match only |
| Tool | exact tool name, for example a file-read primitive |
| Arguments | one relative file path only |
| Authority | read-only |
| Default decision | `ASK`, not `ALLOW` |

Why this is safer than broad `call-tool`:

- it does not permit arbitrary tool names;
- it does not permit shell/process/network/browser actions;
- it does not permit file mutation;
- it does not permit absolute paths;
- it does not permit recursive directory reads;
- it does not trust server-provided descriptions as policy;
- it requires a local policy decision before any future execution;
- it keeps Gateway unable to upgrade Harness decisions.

## REQ-002: policy decision table

| Request class | Example | Decision | Executed | Reason |
| --- | --- | --- | --- | --- |
| MCP status | status inspection | `ALLOW` | false | Existing read-only broker metadata. |
| MCP tool listing | list declared tools | `ALLOW` | false | Existing non-executing discovery. |
| Candidate read request | `repo_public_text_read` for allowlisted relative file | `ASK` | false in M3 | Requires explicit approval in a later implementation. |
| Candidate after approval | same request with valid user approval | future `ALLOW` | future true | Only in later implementation spec, never in M3. |
| Missing server | empty server | `DENY` | false | Ambiguous authority boundary. |
| Unknown server | undeclared server | `DENY` | false | Server not in declared local config. |
| Unknown tool | unlisted tool | `DENY` | false | Tool not allowlisted. |
| Unsafe tool | shell/process/browser/network/write tool | `DENY` | false | Capability class exceeds M3 scope. |
| Absolute path | user-profile or root path | `DENY` | false | Private local state exposure risk. |
| Parent traversal | `../` path | `DENY` | false | Path confinement violation. |
| Directory read | directory target or glob | `DENY` | false | Output and privacy boundary too broad. |
| Untracked private file | local secret/config/runtime file | `DENY` | false | Not a public project surface. |
| Oversized request | excessive path or argument payload | `DENY` | false | Bounded-input violation. |
| Unsafe output | output contains secret shape or private path | future `DENY_RESULT` | future false-to-user | Result is blocked/redacted before display. |
| Server timeout | no response within limit | future `DENY_RESULT` | future attempted | Bounded execution failed safely. |

M3 does not implement the future approval or execution rows. They define the boundary for a later implementation spec.

## REQ-003: output, timeout, audit, and redaction requirements

### Input bounds

Future implementation must reject:

- absolute paths;
- parent traversal;
- empty paths;
- paths longer than a small fixed limit;
- non-text extensions unless explicitly allowed;
- multiple paths in one request;
- free-form tool arguments beyond the declared schema.

### Output bounds

Future implementation must enforce:

- maximum response bytes;
- maximum line count;
- UTF-8 replacement for invalid bytes;
- truncation marker when output is clipped;
- no raw binary display;
- no stdout/stderr passthrough from external tools;
- no full transcript injection into model context.

### Timeout behavior

Future implementation must enforce:

- startup timeout if a later milestone starts an MCP server;
- per-call timeout;
- total operation timeout;
- bounded retry count;
- fail-closed result if any timeout is hit.

### Redaction requirements

Future implementation must block or redact:

- bearer header values;
- token-like values;
- credential key names paired with values;
- private local absolute paths;
- user-profile paths;
- private runtime/audit/metrics/model paths;
- environment variable values;
- chat or pairing identifiers;
- raw tool errors that contain request bodies.

### Audit fields

Every future policy classification should produce prompt-free audit metadata:

- timestamp;
- operation class;
- server name;
- tool name;
- decision;
- executed boolean;
- reason code;
- approval state;
- argument shape, not raw argument value when sensitive;
- output byte count;
- output line count;
- redaction count;
- timeout state;
- truncation state;
- repository-relative target when safe.

Audit must not include token values, environment values, raw output, raw prompts, private paths, or transcripts.

## REQ-004: synthetic fixtures

Before real MCP execution is added, tests should use synthetic fixtures only.

Required fixture families:

| Fixture | Purpose |
| --- | --- |
| allowlisted relative markdown file | Candidate request becomes `ASK`. |
| allowlisted relative source file | Candidate request becomes `ASK`. |
| absolute local path | Request becomes `DENY`. |
| parent traversal path | Request becomes `DENY`. |
| directory target | Request becomes `DENY`. |
| unknown server | Request becomes `DENY`. |
| unknown tool | Request becomes `DENY`. |
| shell/process tool | Request becomes `DENY`. |
| oversized output | Future result truncates or blocks. |
| secret-shaped output | Future result redacts or blocks. |
| malformed JSON arguments | Request becomes `DENY`. |
| timeout fixture | Future result fails closed. |

Fixture tests must not start real external MCP servers and must not read real private files.

## REQ-005: Gateway responsibilities

Gateway is a display and control surface, not an authority escalator.

Gateway must:

- display Harness MCP status and policy classifications;
- show whether a request is `ALLOW`, `ASK`, or `DENY`;
- show `executed=false` for design and dry-run decisions;
- show denial reason codes;
- show redaction/truncation metadata;
- require private-mode auth for all MCP routes;
- never transform `DENY` into `ASK` or `ALLOW`;
- never transform `ASK` into `ALLOW`;
- never send MCP raw output to Telegram by default;
- never expose token values, pair tokens, chat identifiers, private paths, raw stdout/stderr, prompts, or transcripts.

Gateway may later add UI affordances only after Harness exposes safe policy metadata. Gateway UI must not invent MCP policy.

## REQ-006: default posture

The default posture remains:

- MCP status is read-only and non-executing.
- MCP tool listing is read-only and non-executing.
- MCP `call-tool` is denied.
- MCP execution is not enabled by M3.
- Desktop Commander or any other MCP server is not trusted by default.
- Any implementation of `repo_public_text_read` requires a separate spec, tests, and milestone gate.

## Later implementation checklist

A future implementation spec must not begin until it can answer all of these with tests:

1. Which exact server names are allowlisted?
2. Which exact tool names are allowlisted?
3. Which argument schema is accepted?
4. Which paths are eligible?
5. Which outputs are blocked versus redacted?
6. How is user approval represented?
7. Where is prompt-free audit written?
8. How does Gateway display denial without broadening authority?
9. How is timeout handled?
10. How does stack-check prove execution is still disabled unless explicitly enabled?

## Stop rules

Stop and do not implement execution if the next step requires:

- generic `call-tool`;
- shell/process execution;
- write access;
- directory recursion;
- arbitrary server trust;
- raw output display;
- path exposure;
- token or environment value handling;
- Gateway-side authority expansion.
