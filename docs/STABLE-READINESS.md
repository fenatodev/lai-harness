# Stable readiness

This document defines the finite graduation gate from the current beta line to the first stable `v0.4.0` release. It is intentionally narrower than the roadmap: a roadmap item is not a stable-release blocker unless evidence shows the core harness is unsafe, broken, or materially incomplete without it.

## Required core scope

The first stable release must preserve and validate the core that already exists:

- local CLI and VS Code coding modes with repository-confined file tools;
- deterministic `ALLOW` / `ASK` / `DENY` policy and protected-branch guards;
- specs, semantic context, configuration, recovery/checkpoints, run history, metrics, and audit evidence;
- authenticated loopback control plane with shell-free read profiles, isolated write workspaces, structured validation, and hash-bound promotion;
- bounded model evaluation and update intelligence with no automatic update/apply path;
- deterministic release-check, release-pack, release-governance, and project-handoff.

## Graduation gate

All items below are required before changing the public version to `0.4.0`.

### 1. Scope and repository state

- no active spec remains;
- the stabilization milestone has a coherent reviewed scope and a clean tree;
- no known critical/high-severity unresolved defect violates the documented security boundary;
- extracted typed modules do not regress to duplicate implementations in `src/local-agent`;
- strict mypy coverage never shrinks from the milestone ratchet.

### 2. Deterministic quality

- `make milestone-gate` is green; it runs Ruff, pytest, Harness Score, unittest, strict mypy, static checks, publication scan, and VSIX inspection without intentionally duplicating the same expensive suite;
- isolated `install-local.sh` smoke passes and installed deterministic commands work without a model server where documented;
- publication scan and VSIX inspection are clean;
- the final protected PR passes Python 3.11, Python 3.12, Publication gates, and Harness Score L4.

### 3. Operational dogfood

- authenticated `lai doctor` / `lai readiness` succeeds against the supported local endpoint;
- representative read-only and write-capable local flows complete with validation evidence;
- remote read-only and isolated work/promotion boundaries retain their fail-closed tests;
- current baseline-model evaluation has repeated evidence sufficient to expose regressions; model weakness may remain documented, but false success claims or harness safety failures do not.

### 4. Security and authority boundaries

- no remote generic shell is exposed;
- no automatic model download, dependency apply, update apply, commit, push, merge, tag, or release publication authority is introduced implicitly;
- secrets remain excluded from diagnostics, exports, governance output, and publication artifacts;
- protected `main`, strict required checks, linear history, admin enforcement, disabled force pushes, and disabled deletion remain verified.

### 5. Stable release path

- release metadata is intentionally advanced to `0.4.0` only after the stabilization milestone is frozen;
- `lai release-check --target 0.4.0 --json` identifies channel `stable` and expected GitHub prerelease state `false`;
- the exact release pack/VSIX is frozen before tagging;
- tag CI is green;
- the GitHub Release is published from `v0.4.0` with `draft=false` and `prerelease=false`;
- remote governance verifies tag, branch protection, release channel, and VSIX SHA-256;
- final project handoff has no unresolved publication action.

### 6. Documentation

- README, installation, security model, limitations, release docs, and changelog describe the shipped stable behavior rather than planned capability;
- architecture visuals are explicitly reviewed for the stable version marker;
- known limitations remain visible and are not presented as implemented features.

## Explicitly deferred from the v0.4.0 gate

The following may be valuable later, but are **not blockers** for the first stable core unless new evidence changes that decision:

- persistent PWA/Telegram multi-turn sessions and `lai-gateway` product work;
- read-only web search/fetch and browser-action capabilities;
- MCP broker tool execution / Desktop Commander runtime integration beyond non-executing config validation;
- automatic model installer or VS Code Marketplace distribution;
- broader multi-provider support beyond the OpenAI-compatible contract;
- commit/push/PR/merge authority from the remote control plane;
- subagent/delegate orchestration;
- signed releases and provenance attestations;
- archival database storage for runtime history.

These remain roadmap work, not hidden requirements for declaring the coding harness core stable.

## Graduation decision

Promote only when every required section above is supported by current evidence. If a required item fails, fix the evidence-producing defect in a small spec/commit on the stabilization branch. Do not add unrelated roadmap scope merely to delay or decorate the stable release.
