# lai release preflight

Release preflight is a read-only context block injected into release-mode runs before the model reasons.

It exists because small local models can waste rounds probing generic commands such as `pytest --version` or `python -m pytest` even when the repository already declares the correct validation path.

## What it includes

- product name and version;
- repository root, current branch, HEAD, exact tag on HEAD, and latest reachable tag;
- current Git status;
- `lai readiness` overall status and checks;
- preferred validation commands discovered from the repository Makefile.

## Public mode aliases

The `lai` wrapper dispatches mode aliases directly:

```bash
lai diagnose "explain this failure before fixing"
lai ci-fix "repair the failing CI gate"
lai release "check whether beta.11 is ready"
```

These aliases are equivalent to calling `local-agent --diagnose`, `local-agent --ci-fix`, or `local-agent --release` directly.

## Release-mode rule

Release mode should start from the preloaded preflight, inspect only missing evidence, and prefer repository-defined commands such as:

```bash
make check
make test-dev
make test
make validate
```

It must not run `git tag`, `git merge`, `git push`, package upload, or release publication. Those remain human-run commands.


## Deterministic release check

For beta gates and scripted checks, prefer the model-free command:

```bash
lai release-check
lai release-check --json
lai release-check --target 0.4.0-beta.11 --json
```

It reports the expected tag, current branch, HEAD, exact tag on HEAD, latest reachable tag, readiness status, preferred validation commands, and a release-safety check. It does not run validations; use `make validate` separately when validation evidence is needed.

## Read-only remote governance

After GitHub integration/publication steps, use `lai release-governance --target 0.4.0-beta.11 --remote --json` to verify protected-main policy and the pre-release. The remote path performs GitHub API GET requests only and never publishes or changes repository settings.


## Deterministic release pack

`lai release-pack --target 0.4.0-beta.11 --json` writes local publication files outside the repository. Add `--with-vsix` when you want the inspected VSIX in the same pack. It does not tag, merge, push, upload, publish, call the model, or mutate repository files.


## Deterministic project handoff

`lai project-handoff --target 0.4.0-beta.11 --json` renders an offline next-chat handoff. Add `--remote` to include GET-only GitHub release governance evidence. Add `--out /tmp/lai-harness-project-handoff-v0.4.0-beta.11 --force` to write `PROJECT-HANDOFF.md`, `NEXT-CHAT-PROMPT.md`, and `summary.json` outside the repository.
