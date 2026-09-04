# repository migration

The public GitHub repository slug is now `fenatodev/lai-harness`.

The previous slug was `fenatodev/lai-local-agent`. GitHub redirects common web and Git traffic from the old slug after a repository rename, but project documentation and local remotes should use the new slug deliberately.

## current identity

- Product name: `lai harness`
- CLI command: `lai`
- GitHub repository: `fenatodev/lai-harness`
- Compatibility identifiers kept for now: `local-agent`, `lai-chat`, `lai-local-agent.lai`, `~/.config/lai`, `~/.local/share/lai`, and `LAI_*`

## completed migration

The GitHub repository has been renamed from `lai-local-agent` to `lai-harness`, and the local `origin` remote should point to:

```bash
git@github.com:fenatodev/lai-harness.git
```

For HTTPS remotes, use:

```bash
https://github.com/fenatodev/lai-harness.git
```

## optional local folder rename

The local folder may still be named `lai-local-agent`. That does not affect Git behavior. Rename it only when no terminal, editor, or running process is using it:

```bash
cd ~/dev/projects
mv lai-local-agent lai-harness
cd lai-harness
git status --short
git remote -v
```

After renaming the folder, reopen VS Code from the new path.

## compatibility policy

Do not rename the `lai` command. Do not rename user configuration or data directories without a separate migration spec. Do not change the VS Code participant ID until extension migration is planned.

## validation

Run:

```bash
lai version
lai semantics
make validate
```
