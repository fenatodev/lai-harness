# project handoff

`lai project-handoff` creates a portable summary for continuing lai harness work in a new chat, another agent, or a later session.

```bash
lai project-handoff
lai project-handoff --json
lai project-handoff --target 0.4.0-beta.16
lai project-handoff --target 0.4.0-beta.16 --remote --json
lai project-handoff --target 0.4.0-beta.16 --remote --out /tmp/lai-harness-project-handoff-v0.4.0-beta.16 --force --json
lai next-chat --remote --json
```

Default mode is deterministic, model-free, offline, and repository-read-only. `--remote` adds the same GitHub API GET-only verification used by `release-governance --remote`; it never changes repository settings or publishes anything.

## Governance views

Every handoff records the local/offline governance result. With `--remote`, it additionally records:

- remote governance overall status;
- verified protected-main state;
- GitHub pre-release state;
- credential source metadata, never the credential value;
- local and remote VSIX digest evidence when available.

When remote verification is requested, the effective `release_governance_overall` and `manual_actions` come from the remote governance result. The local/offline result remains present separately for auditability.

## What it captures

- product, version, target version and expected tag;
- local checkout, public repository, current branch, HEAD and tag state;
- `lai release-check` status and release phase;
- local and optional remote release-governance state;
- default release-pack location and optional VSIX status;
- safe workspace base and active workspace count;
- active spec summary when one exists;
- operating rules and commands for the next chat.

## Written files

When `--out DIR` is provided, the output directory receives `PROJECT-HANDOFF.md`, `NEXT-CHAT-PROMPT.md`, and `summary.json`. The output directory must be outside the source repository; existing non-empty directories require `--force`.

## Suggested migration flow

```bash
lai release-check --target 0.4.0-beta.16 --json
lai release-governance --target 0.4.0-beta.16 --remote --json
lai project-handoff --target 0.4.0-beta.16 --remote \
  --out /tmp/lai-harness-project-handoff-v0.4.0-beta.16 --force --json
```

Use the default offline handoff when live GitHub state is irrelevant or credentials are unavailable. Use `--remote` when branch protection, Release publication, or artifact digest state affects the next action.
