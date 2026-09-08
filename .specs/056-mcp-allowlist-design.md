# Spec: MCP allowlist design

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Design the first governed step from non-executing MCP visibility toward one narrow class of allowlisted read-only MCP usefulness.

This spec is design-first. It must not enable MCP tool execution by itself.

## Requirements

### REQ-001

Define one candidate read-only MCP operation class and explain why it is safer than broad `call-tool` execution.

### REQ-002

Define a policy decision table covering `ALLOW`, `ASK`, and `DENY` for status, tool listing, candidate execution, malformed requests, unsafe tools, and unsafe outputs.

### REQ-003

Define bounded output requirements, timeout behavior, audit fields, and redaction requirements before any implementation spec can execute a tool.

### REQ-004

Define synthetic fixtures that prove policy and output handling without starting a real external MCP server.

### REQ-005

Define Gateway responsibilities: display classification, show denial evidence, and never broaden a Harness policy decision.

### REQ-006

Document the default posture: MCP `call-tool` remains denied until a later implementation milestone changes it.

## Acceptance Criteria

- The design can be reviewed without enabling execution.
- No MCP server is started by this spec.
- No MCP tool is executed by this spec.
- The future implementation path has explicit policy, audit, output, timeout, and Gateway boundaries.
- The default broker foundation remains non-executing.

## Validation

- `REQ-001`: Design document defines exactly one candidate read-only MCP operation class and explains why broader `call-tool` remains unsafe.
- `REQ-002`: Design document includes a policy decision table covering `ALLOW`, `ASK`, and `DENY` for status, tool listing, candidate execution, malformed requests, unsafe tools, and unsafe outputs.
- `REQ-003`: Design document defines bounded output, timeout behavior, audit fields, and redaction requirements.
- `REQ-004`: Design document defines synthetic fixtures for policy and output handling without starting a real external MCP server.
- `REQ-005`: Design document defines Gateway responsibilities and states that Gateway cannot broaden Harness policy decisions.
- `REQ-006`: Design document and spec state that MCP `call-tool` remains denied until a later implementation milestone changes it.
- Repository gates: publication scan, spec quality sensor, and focused MCP foundation tests pass.

## Context and Constraints

The Harness currently discovers repository-local MCP config and classifies status/list/call operations without execution. Gateway proxies the foundation routes and treats tool execution as denied authority.

## Non-Goals

- Implementing MCP execution.
- Allowing generic shell or process control through MCP.
- File mutation through MCP.
- Passing credential values to the model, Gateway UI, logs, or notifications.
- Treating Desktop Commander or any MCP server as trusted by default.

## Implementation Notes

Prefer design tables and synthetic fixtures first. The first execution milestone should be a separate spec.

## Traceability

- `REQ-001` -> operation-class design note.
- `REQ-002` -> policy decision table.
- `REQ-003` -> audit/output/timeout requirements.
- `REQ-004` -> synthetic fixture plan.
- `REQ-005` -> Gateway responsibility section.
- `REQ-006` -> default posture documentation.

## Completion Evidence

- Design: `docs/M3-MCP-ALLOWLIST-DESIGN.md`.
- Evidence: `docs/M3-MCP-ALLOWLIST-EVIDENCE.md`.
- Focused MCP foundation tests passed while `call-tool` remained `DENY` and `executed=false`.
