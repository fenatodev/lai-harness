# Modes

LAI Harness uses mode-specific skills, tools, token limits, and inference-round limits. The source code is authoritative when this summary and a future version diverge.

| Command | Contract | Available capabilities |
| --- | --- | --- |
| `/explain` | Explain only supplied selection in at most 60 words by default | No tools |
| `/plan` | Short implementation plan without edits | Batch inspect, search |
| `/test` | Execute and diagnose a relevant existing check | Read/project/Git/bash, no writes |
| `/debug` | Reproduce then trace exact source-to-derived values | Batch inspect, search, Git, bash |
| `/review` | At most three evidence-supported findings | Read/search/list/read-only Git |
| `/security` | At most five proven source→flow→sink findings | Read/search/list/read-only Git |
| `/fix` | Narrow diagnosis, edit, and validation | Read/project/Git/edit/bash |
| `/refactor` | Preserve observable behavior and validate | Read/project/Git/edit/create/bash |
| `/implement` | Satisfy all explicit criteria with a batch-oriented patch | Inspect/search/Git/patch/create/bash |

Context commands do not call the model: `/status`, `/metrics`, `/audit`, `/handoff`, and `/clearcontext`.

## Guards

- **Validation guard:** after successful edits in fix, refactor, or implement, the agent cannot conclude until a recognized successful validation command runs.
- **Acceptance guard:** implement detects explicit requests to add/update tests and requires a test-path change.
- **Debug evidence:** debug must both reproduce through `bash` and inspect source before concluding.
- **Evidence gate:** review/security drafts are filtered against collected repository evidence; deterministic filters remove several known unsupported patterns.
- **Post-patch sanity:** JavaScript syntax and added-line checks run first, followed by a compact model classifier. It catches the historical `newError(...)` regression when undeclared.

These mechanisms reduce common failures; they do not prove semantic correctness or security.
