# Protected branch write guard

lai harness blocks repository write tools on protected branches by default.

## Protected branches

The policy blocks `edit`, `create`, `patch`, and `rewrite` on:

- `main`
- `master`
- branches starting with `release/`

This prevents accidental model-generated edits while a release branch or published main commit is being inspected. Read-only commands such as `lai readiness`, `lai doctor`, `lai plan`, `lai diagnose`, and `lai release-check` remain available.

## Safe workflow

Create a disposable or feature branch before using write-capable modes:

```bash
git switch -c test/lai-smoke
lai implement "faça uma alteração pequena e valide"
git diff
git restore .
git switch main
git branch -D test/lai-smoke
```

Use this guard as a backstop, not as a sandbox. Review every diff before keeping model-generated edits.

## Override

For exceptional local maintenance only, set:

```bash
LAI_ALLOW_PROTECTED_BRANCH_WRITES=1 lai implement "..."
```

Do not use the override during release checks or public publication steps.
