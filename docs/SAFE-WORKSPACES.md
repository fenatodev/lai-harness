# Safe workspaces

Safe workspaces are disposable repository copies for dogfooding write modes without touching the source checkout.

They are useful when you want to try `lai implement`, `lai fix`, or `lai ci-fix` but do not want accidental edits in `main` or in a release checkout.

## Create a disposable workspace

```bash
cd ~/dev/projects/lai-local-agent
lai workspace create --name smoke
```

By default, this creates a standalone copy under:

```text
/tmp/lai-harness-workspaces
```

The copy is initialized as its own Git repository on branch:

```text
test/lai-smoke
```

## Use it

```bash
cd /tmp/lai-harness-workspaces/smoke
lai readiness
lai implement "faça uma alteração pequena e valide"
git diff
```

Because the workspace uses `test/lai-smoke`, write tools are allowed without setting `LAI_ALLOW_PROTECTED_BRANCH_WRITES=1`.

## Inspect workspaces

```bash
lai workspace status
lai workspace status --json
```

The status command lists disposable workspaces, their branch, Git status, source commit and path. It does not call the model or mutate the source repository.

## Clean workspaces

```bash
lai workspace clean smoke
```

To remove every disposable workspace under the configured base:

```bash
lai workspace clean --all
```

Clean only removes paths inside the safe workspace base. It refuses outside paths.

## Custom base directory

```bash
LAI_SAFE_WORKSPACE_DIR=/tmp/my-lai-workspaces lai workspace create --name trial
```

or:

```bash
lai workspace create --name trial --base /tmp/my-lai-workspaces
```

The base must be outside the source repository.

## What this does not do

- It does not tag, merge, push, upload, or publish.
- It does not call the model.
- It does not copy untracked files, secrets, virtualenvs, or generated runtime state.
- It does not bypass the protected branch write guard in the source checkout.
