# repository migration

The intended public repository slug is `lai-harness`.

The current repository may still be `fenatodev/lai-local-agent` until the GitHub repository is renamed. GitHub usually redirects clone, fetch, push, and web traffic from the old repository name after a rename, but local remotes and documentation should still be updated deliberately.

## target identity

- Product name: `lai harness`
- CLI command: `lai`
- Intended GitHub repository: `fenatodev/lai-harness`
- Current compatibility identifiers kept for now: `local-agent`, `lai-chat`, `lai-local-agent.lai`, `~/.config/lai`, `~/.local/share/lai`, and `LAI_*`

## manual migration sequence

After a release that prepares the lowercase identity:

1. Rename the GitHub repository from `lai-local-agent` to `lai-harness` in GitHub repository settings.
2. Update the local remote:

```bash
git remote set-url origin git@github.com:fenatodev/lai-harness.git
```

or, for HTTPS:

```bash
git remote set-url origin https://github.com/fenatodev/lai-harness.git
```

3. Optionally rename the local folder:

```bash
cd ~/dev/projects
mv lai-local-agent lai-harness
cd lai-harness
git status --short
git remote -v
```

4. Run the validation gate:

```bash
make validate
```

5. Update repository links in documentation only after the remote rename is complete.

## compatibility policy

Do not rename the `lai` command. Do not rename user configuration or data directories without a separate migration spec. Do not change the VS Code participant ID until extension migration is planned.
