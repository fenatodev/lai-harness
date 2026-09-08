# lai harness roadmap

This roadmap describes the current post-A12 state and future direction. It does not grant runtime capability by itself.

## Current status

All non-experimental September 2026 replan milestones are complete in the local repository package and have passed `make milestone-gate` at their milestone boundaries.

| Milestone | Name | Status | Specs |
| --- | --- | --- | --- |
| A0 | autonomy architecture replan | complete | 059 |
| A1 | trajectory and budgets | complete | 060, 061 |
| A2 | authority and credentials | complete | 062, 063 |
| A3 | sandbox and primitives | complete | 064, 065 |
| A4 | local web chat | complete | 066, 067, 068 |
| A5 | deterministic code graph | complete | 069 |
| A6 | governed egress, browser and external actions | complete | 070, 071, 081 |
| A7 | sandboxed MCP execution | complete | 072 |
| A8 | model profiles and skills | complete | 073, 074 |
| A9 | forks and delegates | complete | 075, 076 |
| A10 | trusted host | experimental draft | 077 |
| A11 | isolated computer use | experimental draft | 078 |
| A12 | distribution and validation | complete | 079, 080 |

## Public capability line

The current public line should document A0-A9 and A12 as implemented. A10 and A11 must remain explicitly experimental until a maintainer makes a separate risk decision, implements the specs, and validates them.

## Near-term maintenance priorities

1. Review and commit the consolidated A0-A12 local diff.
2. Push through the protected review/CI process only after maintainer approval.
3. Keep documentation aligned with `lai gateway-contract --json`, `lai validation matrix --json` and tests.
4. Continue reducing monolith risk by extracting deterministic subsystems only when behavior is already stable.
5. Add real integrations only after a dedicated threat model, fixture suite and fail-closed contract exist.

## Deferred or out of scope

- Real credentials and account actions.
- Real browser automation with personal profile or login.
- Generic MCP server startup from repository config.
- Unbounded delegate swarms.
- Automatic model download, router or cloud fallback.
- Autoupdate, tag, push, release or branch-protection mutation from local commands.

## Historical planning

Detailed planning records remain in `docs/PROJECT-PLAN-2026-09.md`, `docs/EXECUTION-BACKLOG-2026-09.md`, `docs/PLANNING-MANIFEST-2026-09.json`, `docs/DECISION-LOG-2026-09.md` and the `.specs/` directory. Prefer the current README and documentation portal for public capability claims.
