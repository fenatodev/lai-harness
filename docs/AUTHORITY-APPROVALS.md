# Authority, grants and approvals

Authority is represented as explicit records and deterministic checks, not as text in a prompt.

## Current authority presets

The control plane exposes authority presets for current safe/work-sandbox behavior. They describe capabilities such as shell, MCP, source checkout writes and promotion boundaries. They do not grant additional authority by themselves.

## Approval intents

Approval intents are:

- versioned;
- hash-bound to the requested payload;
- tied to principal, workspace, repository, branch, Git status and policy preconditions;
- TTL-bound;
- use-once;
- revocable;
- persisted outside the repository.

An approval intent does not execute arbitrary tool payloads. Replay, hash mismatch, workspace drift, policy drift and revocation fail closed.

## Credentials

The credential broker foundation supports opaque refs and receipts through a fake adapter. Real credentials are not enabled. Public status and receipts must not expose canary values or secret material.

## External actions

The current external action adapter is `fake_git_remote` for `push_branch` simulation. It is hash-bound, baseline-bound, expected-remote-SHA-aware, TTL-bound and use-once. It produces receipts and treats `outcome_unknown` as terminal without automatic retry.

No real GitHub push, PR, merge, tag, release or remote settings mutation occurs through this package.

## Promotion

Approved workspace promotion remains the Harness-owned integration path. It requires exact patch hash, validation state and source cleanliness. Stale hashes and source drift fail closed.
