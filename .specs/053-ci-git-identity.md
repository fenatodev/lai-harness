# Spec: CI git identity for context tests

Status: complete
Mode: fix

## Problem

The v0.4.8 pull request CI failed on Python 3.11 and Python 3.12 because context-diff tests create commits inside temporary Git repositories. GitHub-hosted runners do not guarantee `user.name` and `user.email`, so `git commit -q -m init` failed with author identity errors even though local validation passed.

## Requirements

- REQ-001: Configure a deterministic local Git identity for every temporary test repository created by `LocalAgentTest.setUp`.
- REQ-002: Keep the identity scoped to the temporary repository, not global runner configuration.
- REQ-003: Preserve the metadata-only context behavior unchanged.
- REQ-004: Validate the previously failing context tests and rerun the release milestone gate before updating the pull request.

## Non-goals

- Do not weaken failing tests.
- Do not change runtime behavior, release version, Gateway compatibility, model selection, or CI branch protection.
- Do not tag or publish the release before PR CI, main integration, and tag CI are green.

## Validation

- Reproduced the pull request failure from GitHub Actions: Python 3.11 and Python 3.12 failed because `git commit -q -m init` in temporary repositories had no local author identity.
- Focused failing tests passed: `3 passed in 0.44s`.
- Broader context regression passed: `24 passed, 138 deselected, 5 subtests passed in 1.81s`.
- `git diff --check` passed.
- Full `make milestone-gate` passed in 168.21s: Ruff green, `311 pytest tests + 144 subtests`, Harness Score L4 `100/108`, `311 unittest tests`, strict mypy over seven files, publication scan clean, and VSIX inspection passed.
- No runtime behavior, release version, Gateway compatibility, model selection, branch protection, tag, or GitHub Release was changed.
