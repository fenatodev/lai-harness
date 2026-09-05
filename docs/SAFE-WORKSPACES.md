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

## Automatic control-run workspaces

Starting with beta.14, remote `implement`, `fix`, `refactor`, and `ci-fix` control runs create a unique safe workspace automatically before the model starts. The control child uses that copy as its repository root; the source checkout is not the child's working tree.

Remote validation runs against the safe workspace through the configured Docker sandbox. At completion, the control-run record returns bounded Git status, changed paths, and diff evidence. The workspace path is operational evidence, not an approval to copy changes into the source repository.

Work-result promotion is intentionally a separate future capability. Until that protocol exists, review the returned diff and apply equivalent changes through the normal protected feature-branch workflow rather than treating a control-run workspace as authoritative source state.


## Approved promotion

Starting with beta.15, a successful control-run workspace may expose a promotion proposal. The proposal is based on the source SHA/branch/clean state captured by the control server before the model starts and on a complete bounded patch reconstructed from Git, not on mutable workspace metadata or the display diff.

Approval supplies the exact patch SHA-256. The server recomputes that patch, repeats `full` validation in the fixed Docker sandbox, rechecks source drift, and creates a deterministic `lai/promotion-<run-id>` branch in a worktree under `$LAI_DATA_DIR/promotions`. It applies with `git apply --check` followed by `git apply` and verifies the resulting patch hash. The active source checkout is never switched or edited.

Promotion is intentionally not commit/push/merge. The resulting worktree is the durable integration boundary for later review and future Git-governance cuts.
