# project handoff

`lai project-handoff` creates a portable summary for continuing lai harness work in a new chat, another agent, or a later session.

```bash
lai project-handoff
lai project-handoff --json
lai project-handoff --target 0.4.0-beta.7
lai project-handoff --target 0.4.0-beta.7 --out /tmp/lai-harness-project-handoff-v0.4.0-beta.7 --json
lai next-chat --json
```

The command is deterministic. It does not call the model, create tags, merge branches, push, upload assets, publish a GitHub Release, run validation commands, or mutate repository files.

## What it captures

- product, version, target version and expected tag;
- local checkout, public repository, current branch, HEAD and tag state;
- `lai release-check` status and release phase;
- `lai release-governance` status and manual GitHub actions;
- default release-pack location and optional VSIX status;
- safe workspace base and active workspace count;
- active spec summary when one exists;
- operating rules for the next chat;
- commands to re-establish context safely.

## Written files

When `--out DIR` is provided, the output directory receives:

- `PROJECT-HANDOFF.md` — full human-readable handoff;
- `NEXT-CHAT-PROMPT.md` — small prompt block to paste into a new chat;
- `summary.json` — machine-readable handoff metadata.

The output directory must be outside the source repository. Existing non-empty directories require `--force`.

## Suggested migration flow

Before leaving a long chat:

```bash
lai release-check --target 0.4.0-beta.7 --json
lai release-governance --target 0.4.0-beta.7 --json
lai project-handoff --target 0.4.0-beta.7 --out /tmp/lai-harness-project-handoff-v0.4.0-beta.7 --force --json
```

In the new chat, paste `NEXT-CHAT-PROMPT.md` or tell the assistant to read the generated `PROJECT-HANDOFF.md` path using Remote Desktop Commander.
