# PR62: Governed structured development progress

Status: active

## Goal

Complete inspect/read → decide → semantic write → validate → repair → terminal review
with a slow local model, preserving the current sandbox and capability ceilings.
This revises the in-progress write-only proposal; it does not restart the work.

## Requirements

- REQ-001: Work pre-write turns require structured tool progress. Compact exploration
  must not impose the old 96-token remote cap on actual edits. A truncated response
  is discarded; one bounded retry offers an action or necessary prerequisite read,
  not an unbounded analysis loop. Local impossibility is structured; remote profiles
  gain no new tools. A terminal impossibility is not a successful implementation.
- REQ-002: Enforce offered/mode capabilities at dispatch. Bounded prerequisite
  inspection (AGENTS.md, stale/unread write targets) remains possible during action
  and repair phases; it cannot reset the exploration or no-progress budget.
- REQ-003: Identical edits/rewrites, already-applied or net-zero patches do not write
  bytes or count as progress. Repeated failed/no-op calls terminate boundedly;
  invalid arguments yield recoverable tool feedback instead of crashing.
- REQ-004: Successful writes preserve validation and correction. Failed validation
  allows bounded inspection of concrete failures; no new shell or remote authority.
- REQ-005: The whole sandboxed work-run has a finite budget appropriate for multiple
  slow model turns, distinct from read-only and per-validation timeouts.
- REQ-006: Regression coverage plus real local Qwen via Gateway/Harness must produce
  changed isolated content, successful validation and terminal review. Source hashes
  remain unchanged; no promotion, apply, commit, push, PR or merge by the agent.

## Validation

Focused guard, policy, control-plane and fake-server tests; repository checks;
real sandboxed local-model dogfood. Fixtures alone are not completion evidence.

## Runtime-entrypoint correction found during integration

The old remote entrypoint `/workspace/src/local-agent` assumes every target is
itself a Harness repository and lets target code impersonate the executor.
Use the serving Harness's own runtime files, mounted individually read-only
under /lai-harness, and its shipped skills under a separate read-only mount.
Never execute an entrypoint supplied by the target checkout. Source and sandbox
mount isolation, non-root execution and no-network policy stay unchanged.
