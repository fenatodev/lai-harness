# Spec: structured context dogfood

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Improve LAI's deterministic context preparation so constrained local models spend fewer rounds rediscovering repository structure during `plan`, `diagnose`, `review`, and related remote control tasks.

This milestone should be driven by observed dogfood failures and measured tool-call reduction, not by speculative indexing features.

## Requirements

### REQ-001

Capture at least two current dogfood tasks where the model performs unnecessary repository-discovery work or produces low-value status answers because structured context is insufficient.

### REQ-002

Enhance deterministic context summaries using metadata-only views. The summaries may include repository map, changed-path groups, symbol navigation, validation/test inventory, recent run metadata, or process/runtime status, but must not include raw source bodies, raw diffs, stdout, stderr, transcripts, credentials, or private paths.

### REQ-003

Add or update tests proving that the improved summaries are bounded, deterministic, repository-confined, and secret-free.

### REQ-004

Add model-evaluation or dogfood evidence comparing before/after behavior on the selected tasks. Evidence should track tool calls, runtime, truncation/retry behavior, and answer correctness.

### REQ-005

Preserve existing policy boundaries. This milestone must not add shell authority, MCP tool execution, browser actions, dependency mutation, model download, commit, push, PR, tag, or release authority.

### REQ-006

Update user-facing documentation only where the new context behavior changes operator expectations or available commands.

## Acceptance Criteria

- At least two dogfood tasks are documented with baseline behavior and improved behavior.
- Focused tests cover the touched context summaries.
- Existing context commands remain deterministic and model-free.
- New output remains bounded and secret-free under publication scan.
- Model-eval or dogfood records show an improvement in at least one measurable dimension without a correctness regression.
- `make check` passes before integration; `make milestone-gate` is required before PR or release decisions.

## Validation

- `REQ-001`: baseline dogfood notes or fixtures for at least two selected tasks.
- `REQ-002`: focused context renderer/ranking tests plus relevant `lai context ... --json` command output for changed views.
- `REQ-003`: tests proving bounded, deterministic, repository-confined, secret-free context output.
- `REQ-004`: fixed model-eval or dogfood comparison records for the selected tasks.
- `REQ-005`: policy, contract, and publication tests showing no authority expansion.
- `REQ-006`: documentation diff review and publication scan when operator-facing behavior changes.
- Full gate before integration: `make check` and `make milestone-gate`.

## Context and Constraints

LAI already has metadata-only context commands such as `context map`, `context changes`, `context diff`, `context checks`, `context runs`, and `context symbols`. The next milestone should improve usefulness and injection quality, not add an unrelated index.

Historical workspace state and session text are advisory and untrusted. Current repository evidence always wins.

## Non-Goals

- Embeddings, vector databases, external indexes, or persistent semantic services.
- Broad background scanning of user files.
- MCP tool execution, shell execution, browser actions, dependency mutation, commits, pushes, PRs, tags, or releases.
- Changing the default model baseline.
- Gateway UI polish unless it exposes the improved Harness context behavior for real dogfood.

## Implementation Notes

Likely affected areas include context ranking, context command renderers, structured summary injection, model-evaluation fixtures, and documentation under `docs/CONTEXT-INTELLIGENCE.md`.

Start by measuring the current failure mode. Do not implement a new context feature until the dogfood task proves why it is needed.

## Traceability

- `REQ-001` -> dogfood baseline notes or fixtures.
- `REQ-002` -> context renderer/ranking tests.
- `REQ-003` -> bounded/secret-free context tests.
- `REQ-004` -> model-eval or dogfood comparison records.
- `REQ-005` -> policy, contract, and publication tests.
- `REQ-006` -> documentation diff and publication scan.

## Initial Dogfood Candidates

The first baseline tasks should be drawn from real operator workflows:

1. Planning from a clean repository state without broad repeated doc inspection.
2. Read-only diagnose of readiness/model/MCP state without unnecessary model rounds.
3. Narrow implementation planning for context-intelligence code/tests with fewer inspect/search cycles.

Current baseline metadata observed during planning:

- Repository map: 149 tracked files grouped by directory.
- Checks summary: 15 test files plus `test`, `check`, `validate`, and `milestone-gate` targets.
- Runs summary: 121 recent metadata-only run records/checkpoints.

Initial dogfood evidence is recorded in `docs/M1-DOGFOOD-EVIDENCE.md`:

- Local `plan` with active spec improved from immediate context-window failure to deterministic completion with no model calls, no tool calls, and no truncation for narrow milestone-orientation requests.
- Local `diagnose` for readiness/model/MCP improved from context-window failure to deterministic completion with no model or tool calls.

These results satisfy the first evidence cut for narrow deterministic preflight behavior. Remaining M1 work should focus on broader model-backed planning tasks that do not match the preflight conditions.

## Validation Evidence

- Baseline and after evidence recorded in `docs/M1-DOGFOOD-EVIDENCE.md`.
- Focused context/spec/plan/diagnose pytest subset passed: 35 passed, 136 deselected, 5 subtests.
- Full unittest suite passed: 323 tests.
- Static checks passed: compileall, `py_compile`, Node syntax, shell syntax, JSON parse, `git diff --check`, and publication scan.
- Local `diagnose` readiness/model/MCP dogfood completed with zero model calls and zero tool calls.
- Local active-spec milestone `plan` dogfood completed with zero model calls, zero tool calls, and no truncation under the narrow preflight conditions.
