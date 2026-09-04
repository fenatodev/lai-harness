# lai harness

**Local-first coding harness for constrained LLMs.**

Small local models become much more useful when the agent architecture is optimized around them. lai harness is an experimental VS Code coding harness designed around constrained context, low tool-schema overhead, batch operations, evidence gates, validation guards, metrics, and forensic auditing.

lai harness complements high-context cloud agents. It targets fast, bounded local cycles—planning, debugging, focused implementation, testing, and review—and can leave a compact handoff for another agent or a future session.

## Why lai harness

General-purpose agent harnesses can spend a large share of a small model's budget on prompts, tool schemas, and repeated inference rounds. lai harness reduces that overhead with mode-specific tools and prompts, batch inspection and patching, compact workspace state, and deliberately short outputs.

## Architecture

```text
VS Code @lai participant
        │ selection, diagnostics, task
        ▼
local-agent (Python standard library)
        ├── mode-specific skill and tool schemas
        ├── repository-confined file tools
        ├── validation, acceptance, evidence, and sanity gates
        ├── workspace state, metrics, and audit JSONL
        └── authenticated OpenAI-compatible HTTP request
                         │
                         ▼
                     llama.cpp
                         │
                         ▼
                  user-supplied GGUF
```

See [Architecture](docs/ARCHITECTURE.md) for the detailed data flow, [Branding](docs/BRANDING.md) for naming rules, [Semantic code contracts](docs/SEMANTIC-CODE-CONTRACTS.md) for subsystem navigation metadata, and [Beta readiness](docs/BETA-READINESS.md) for the beta.8 release posture.

## Features

- canonical lai harness branding while preserving the `lai` command and compatibility identifiers;

- ten compact tools, selected per mode;
- multi-file `inspect` and transactional exact-replacement `patch`;
- repository-root path confinement and explicit symlink checks for batch patches;
- centralized `ALLOW` / `ASK` / `DENY` policy with read-only Git inspection and human-gated Git mutation;
- validation guard after edits in implementation modes;
- acceptance guard for explicitly requested test changes;
- evidence-driven debug, review, and security modes;
- deterministic plus model-assisted post-patch sanity checking;
- local JSONL metrics and forensic audit records;
- persistent, Git-aware workspace handoff;
- repository-local `.specs/` with stable `REQ-NNN` traceability;
- deterministic `lai spec` inspection with quick/full workflow guidance;
- policy decisions and user-action lifecycle outcomes in the audit trail;
- crash-safe workspace checkpoints with explicit, drift-checked `lai recovery` / `lai resume`;
- deterministic, explainable context ranking with bounded metadata-only `lai context`;
- validated configuration diagnostics with secret-safe `lai config`;
- deterministic `lai model` benchmark planning, JSONL samples, and local scoring;
- deterministic `lai semantics` subsystem map for model-friendly code navigation;
- deterministic `lai runs` / `lai run show` browser and sanitized `lai run export` bundle for local run history;
- deterministic `lai readiness` environment and repository health check;
- focused `diagnose`, `ci-fix`, and `release` skills plus release preflight gates for safer beta operations;
- deterministic `lai project-handoff` / `lai next-chat` for portable long-session migration;
- no Python package dependencies in the current harness.

## Quick start

Requirements: Python 3.11+, Git, ripgrep, VS Code with Chat Participant API support, and an authenticated OpenAI-compatible `llama.cpp` server.

```bash
git clone https://github.com/fenatodev/lai-harness.git
cd lai-harness
./scripts/install-local.sh
mkdir -p ~/.config/lai
umask 077
printf '%s' 'replace-with-a-random-local-key' > ~/.config/lai/llama-api-key
```

Configure `~/.config/lai/config.toml`, `LAI_*` environment variables, or leading CLI flags as needed. Precedence is `CLI > environment > TOML > defaults`. Then run `lai doctor`, install the extension from source, reload VS Code, open a Git repository, and try:

```text
@lai /plan add a focused regression test for the parser
@lai /debug reproduce why the timeout becomes NaN
@lai /diagnose explain why the CI is failing
@lai /ci-fix repair the failing publication gate
@lai /release verify whether beta.8 is ready
@lai /implement add the requested test and minimal fix
@lai /review review my current Git changes
@lai /audit
lai spec
lai config
lai context "repair parser timeout"
lai semantics
lai runs
lai run last
lai readiness
lai release-check --target 0.4.0-beta.8 --json
lai release-pack --target 0.4.0-beta.8 --with-vsix --json
lai release-governance --target 0.4.0-beta.8 --remote --json
lai project-handoff --target 0.4.0-beta.8 --json
lai recovery
# if recovery reports a compatible interrupted run:
lai resume
```

Read the complete [Installation](docs/INSTALLATION.md) and [Quick start](docs/QUICKSTART.md) guides before using write-capable modes.

Release operators should use `lai release-pack`, [Release pack](docs/RELEASE-PACK.md), [Release notes](docs/RELEASE-NOTES.md), [Release checklist](docs/RELEASE-CHECKLIST.md), and [GitHub publishing metadata](docs/GITHUB-PUBLISHING.md) before creating a GitHub Release. Write-capable local testing should follow [Protected branch write guard](docs/PROTECTED-BRANCH-WRITES.md).

## Modes

| Mode | Purpose | Writes files |
| --- | --- | --- |
| `/explain` | Explain the current selection | No |
| `/plan` | Produce a short grounded plan | No |
| `/test` | Run and diagnose an existing check | No |
| `/debug` | Reproduce and trace an exact failure chain | No |
| `/diagnose` | Diagnose symptoms, logs, environment drift, or run state before fixing | No |
| `/review` | Review current code or Git changes | No |
| `/security` | Trace evidence-backed security findings | No |
| `/release` | Verify release readiness and produce human-run release commands | No |
| `/fix` | Apply and validate a focused fix | Yes |
| `/ci-fix` | Repair a concrete failing validation or CI gate | Yes |
| `/refactor` | Make a behavior-preserving structural change | Yes |
| `/implement` | Complete explicit criteria and validate them | Yes |
| `/status` | Show workspace state | No |
| `/metrics` | Summarize recent local measurements | No |
| `/audit` | Show the latest auditable run | No |
| `/handoff` | Show or annotate compact shared context | State only |
| `/clearcontext` | Clear persisted workspace context | State only |

Detailed contracts are in [Modes](docs/MODES.md).

## Security boundary

lai harness is **not a sandbox**. Every builtin tool action crosses a deterministic policy boundary. Safe actions are `ALLOW`, sensitive Git/dependency mutations are `ASK` and stop for explicit user action, and selected destructive commands are `DENY`. However, allowed `bash` commands still execute with the user's OS permissions and command inspection cannot cover every equivalent spelling or indirect action. Use lai harness only in trusted, disposable or backed-up workspaces under a least-privilege account. Review [Security model](docs/SECURITY-MODEL.md).

Never commit API keys, state, metrics, audit logs, model files, or real project handoffs. The included `.gitignore` blocks their common locations.

## Observability and handoff

Each run gets a `run_id`. Metrics record inference/tool timing, token usage, tool rounds, and schema counts. Audit events associate patches with before/after SHA-256 hashes, sanity state, validation results, and final status. These files can contain paths and task context and remain local by default.

Workspace handoff is written to `current-context.md` and JSON. A receiving agent must verify it against the actual Git branch, status, and files before acting. Runtime checkpoints are separate: they are atomic, workspace-scoped recovery records used only for explicit resume after branch/status/hash compatibility checks. See [Context intelligence](docs/CONTEXT-INTELLIGENCE.md), [Observability](docs/OBSERVABILITY.md), [Recovery](docs/RECOVERY.md), and [Handoff](docs/HANDOFF.md).

## Experimental results

On one development machine and synthetic fixture, observed runs were approximately 8–10 seconds for review, 17 seconds for planning, 22 seconds for debugging, and 32 seconds for implementation with sanity checking. One implementation fixture fell from roughly 14 API calls and 15 tool calls to about 5 API calls and 3 tool calls after batch-oriented changes.

These are historical, hardware-specific observations—not universal benchmarks or performance promises. See [Benchmarks](docs/BENCHMARKS.md).

## Limitations

- Linux/WSL-first development workflow;
- launcher examples assume `llama.cpp`, while the HTTP client only requires a compatible endpoint;
- model and prompt behavior vary substantially;
- shell policy is structured as `ALLOW` / `ASK` / `DENY`, but command detection is not containment;
- no extension marketplace package or automatic model installer;
- metrics/audit retention is basic and local;
- no guarantee that model output is correct, safe, or license-compatible.

## Roadmap and project history

The next priorities are a stronger execution boundary, configuration validation, broader fixtures, packaging, and cleaner provider abstraction. See [Roadmap](ROADMAP.md), [Design decisions](docs/DESIGN-DECISIONS.md), and the failure-driven [Development journey](docs/DEVELOPMENT-JOURNEY.md).

## License and third parties

Original LAI code is released under the [MIT License](LICENSE). This does not license or redistribute VS Code, llama.cpp, Ministral/Mistral models, GGUF files, model templates, or any other third-party component. Users must obtain them separately and comply with their respective terms. See [Third-party software](THIRD_PARTY.md).

## Contributing

Focused issues, reproducible fixtures, security reports, and measured improvements are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

### Safe dogfood workspace

Use a disposable workspace when testing write-capable modes without touching `main`:

```bash
lai workspace create --name smoke
cd /tmp/lai-harness-workspaces/smoke
lai implement "faça uma alteração pequena e valide"
git diff
```

See [Safe workspaces](docs/SAFE-WORKSPACES.md).
