# PR60: Pre-Write No Progress

## Goal
Impede loops of implement/fix/refactor/ci-fix that consume rounds without progress when the model responds without tool call before any write.

## Mode
quick

## Status
active

## REQ-001
Before any successful write, a response without tool call should count as `pre_write_no_progress`.

## REQ-002
Allow at most one explicit correction requiring write tool or `IMPLEMENTATION_IMPOSSIBLE`.

## REQ-003
If the next response continues without tool call/write, terminate with specific `pre_write_no_progress` reason instead of `overall_round_limit_reached`.

## REQ-004
After a successful write, preserve the current validation, test, and guard flow.

## REQ-005
Do not alter `PRE_WRITE_EXPLORATION_BUDGET` nor `max_rounds`.

## Acceptance Criteria

1. A model response without tool call before any write counts as `pre_write_no_progress`.
2. Only one explicit correction requiring write tool or `IMPLEMENTATION_IMPOSSIBLE` is allowed.
3. Subsequent responses without tool call terminate with `pre_write_no_progress` reason.
4. Successful write maintains current validation, test, and guard flow.
5. `PRE_WRITE_EXPLORATION_BUDGET` and `max_rounds` remain unchanged.

## Validation

1. Verify that a response without tool call before any write triggers `pre_write_no_progress` (REQ-001).
2. Confirm that only one explicit correction requiring write tool or `IMPLEMENTATION_IMPOSSIBLE` is permitted (REQ-002).
3. Ensure that subsequent responses without tool call terminate with `pre_write_no_progress` reason instead of `overall_round_limit_reached` (REQ-003).
4. Validate that successful write preserves current validation, test, and guard flow (REQ-004).
5. Check that `PRE_WRITE_EXPLORATION_BUDGET` and `max_rounds` are not altered (REQ-005).
