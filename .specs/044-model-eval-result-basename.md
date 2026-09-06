# Spec: model eval result basename resolution

## Metadata

- Mode: `quick`
- Status: `complete`

## Goal

Make the documented `lai model score <result.jsonl>` form resolve saved result basenames from LAI's model-eval data directory when no same-named repository file exists.

## Requirements

### REQ-001

Resolve only an existing regular file under the repository or LAI model-eval data directory, preferring an existing repository path and otherwise falling back to the saved-result directory without weakening path confinement.

## Acceptance Criteria

- a saved result basename scores successfully from the default model-eval data directory;
- repository-relative result files keep working;
- paths outside the repository/data boundary remain rejected.

## Validation

- `REQ-001`: focused model-eval basename/path regression plus Ruff and deterministic static checks.


## Validation Evidence

- Reproduced the failure with persisted model-eval basenames: the resolver returned a nonexistent repository candidate before checking the saved-result directory.
- The resolver now considers only existing regular files before applying repository/model-eval confinement, preserving repository-relative behavior and outside-path rejection.
- Focused regressions: 3 passed; Ruff, compile/static checks, and `git diff --check` passed.
- Dogfood with all persisted result basenames now scores 10 Ministral records successfully with 5/5 scenario coverage and `decision_eligible: yes`.
- No full milestone gate was rerun because this quick fix is narrowly covered and the base commit `3c34609` had just passed `make milestone-gate`; no push/PR/tag/release mutation occurred.
