# Spec: Context Intelligence

## Metadata

- Mode: `full`
- Status: `complete`

## Goal

Reduce model-driven repository discovery by ranking a small set of explainable file candidates before inference, without adding embeddings, vector databases, dependencies, or new model-facing tool schemas.

## Requirements

### REQ-001

Build a deterministic bounded repository file inventory that excludes Git metadata, common generated/dependency directories, symlinks, and paths outside the repository.

### REQ-002

Rank candidate files using explicit weighted signals from the current task, live Git changes, verified recent/modified workspace state, active spec references, and known project manifests.
### REQ-003

Task/path matches and bounded content matches must increase relevance without reading unbounded file contents or making persisted context authoritative.

### REQ-004

Ranking output must expose a stable score and human-readable reasons for every returned candidate, with deterministic tie-breaking.

### REQ-005

Only the highest-ranked bounded candidate metadata may be injected into model context; candidate file contents are not preloaded automatically.

### REQ-006

Context intelligence must be enabled for `plan`, `debug`, `fix`, `implement`, and `refactor` while preserving each mode's existing tool schemas and guards.

### REQ-007

`lai context <task>` must report the ranked candidates deterministically without starting or probing the model server.

### REQ-008

Missing Git metadata, unreadable files, malformed workspace state, and unsupported file types must degrade safely without escaping repository confinement or failing the whole run.
### REQ-009

The implementation must remain standard-library-only and must not add embeddings, vector stores, MCP, delegates, learning, or automatic tool-call replay.

## Acceptance Criteria

- Relevant task-named and Git-changed files rank above unrelated repository noise.
- Recent and modified workspace files contribute only bounded advisory weight.
- Active spec path references contribute a distinct ranking reason.
- Ranking is stable for identical repository state and task input.
- Injected context contains candidate metadata only and stays within a fixed character budget.
- `lai context` works with the model server unavailable.
- Existing mode, policy, recovery, validation, and publication gates remain green.

## Validation

- `REQ-001`: bounded inventory and exclusion tests.
- `REQ-002`, `REQ-003`: ranking-signal and ordering tests.
- `REQ-004`: deterministic score/reason tests.
- `REQ-005`, `REQ-006`: prompt-injection integration tests by mode.
- `REQ-007`: deterministic CLI test with server unavailable.
- `REQ-008`: degraded-input and confinement tests.
- `REQ-009`: dependency/publication regression checks.

## Context and Constraints

Alpha.9 adds explicit crash recovery but intentionally reserves context ranking and repository intelligence for alpha.10. Current discovery depends on `project`, textual search, and `inspect`, so the model often spends inference rounds deciding which files to inspect. The new layer must reduce that discovery cost without turning advisory context into authority.

## Non-Goals

- Embeddings, semantic vector search, vector databases, or external indexing services.
- New model-facing tool schemas solely for ranking.
- Automatic file-content preload beyond existing active-spec and handoff behavior.
- MCP, plugins, delegates, learning, or automatic strategy selection.
- Sandbox/container execution or approval UI.

## Implementation Notes

Prefer live Git evidence and current task signals over persisted workspace hints. Use a small bounded inventory, bounded text sampling, explicit weights, deterministic sorting, and compact metadata-only rendering. Existing repository rules, active spec, policy, recovery, and live tool evidence always override ranked candidates.
## Traceability

- `REQ-001` -> inventory exclusion/bounds tests
- `REQ-002` -> weighted signal tests
- `REQ-003` -> task/path/content relevance tests
- `REQ-004` -> stable score/reason ordering tests
- `REQ-005` -> bounded metadata rendering tests
- `REQ-006` -> mode prompt-injection integration tests
- `REQ-007` -> `lai context` deterministic CLI test
- `REQ-008` -> degraded Git/state/file tests
- `REQ-009` -> full validation and publication scan
