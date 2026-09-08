# Sessions, forks and delegates

## Sessions

Control-plane sessions are repository-scoped, persistent and bounded. Session history is treated as untrusted context. Unknown sessions, unsafe IDs, symlinks and future schemas fail closed.

## Fork experiments

Session fork comparison creates independent child sessions from a common base snapshot. It does not copy tokens, approvals, grants, processes, PIDs or workspace paths.

Comparison is sanitized and conservative:

- common-base comparison first;
- validation and patch hash before cost;
- different results remain inconclusive;
- `winner` is `null` in the current implementation;
- integration still requires hash-bound promotion.

## Delegate waves

Delegate waves are fixture-only, bounded and serial by default. They validate DAG dependencies, ownership, budget, path bounds, collisions and cancellation. They do not create a real swarm, grant new authority or run subagents outside the Harness boundary.

Use these features as workflow contracts and safety fixtures, not as proof that arbitrary parallel agent delegation is enabled.
