# Spec: Update intelligence

## Metadata

- Mode: `full`
- Status: `complete`
- Target: `0.4.0-beta.21`

## Goal

Add a bounded, model-free update radar that tells operators which LAI dependencies and trusted upstream references changed, highlights known security information where an official source exposes it, and never applies updates automatically.

## Context and Constraints

- Release beta.20 is complete and the repository starts this cut from protected, synchronized `main`.
- Runtime remains Python standard-library-only.
- Network access must be explicit and read-only in effect.
- Upstream endpoints are code-defined/manifest-defined trusted sources; callers and models cannot provide arbitrary URLs.
- Update intelligence is evidence for a future spec/PR, not authority to download, install, edit, commit, push, merge, tag, or publish.
## Requirements

### REQ-001
**Trusted update manifest.**

Version a repository manifest that enumerates each tracked source by stable id, category, source type, and trusted upstream identity. Unknown source types, duplicate ids, malformed repository/package names, or unsupported detector types fail closed.

### REQ-002
**Offline inventory.**

`lai update plan` renders the tracked dependency/upstream inventory without contacting the network, local model, or local model server.

### REQ-003
**Explicit bounded remote check.**

`lai update check --remote` may contact only fixed official HTTPS hosts required by the trusted source types. Requests are bounded by timeout and response size; arbitrary caller/model URLs, redirects to untrusted hosts, credentials for public update feeds, and generic fetch are forbidden.

### REQ-004
**Current-version evidence.**

Exact Python development pins and the Harness Score pin are derived from repository files. The configured llama.cpp runtime build is derived from authenticated local `/props` when available; missing runtime evidence is reported as unknown rather than guessed.
### REQ-005
**Version and security classification.**

Tracked installed dependencies report current/latest status. PyPI-backed pins also report vulnerability metadata for the exact installed version when PyPI provides it. Dependabot-managed GitHub Actions are identified as externally managed rather than duplicated by a second updater.

### REQ-006
**Reference-upstream radar.**

Trusted coding-agent/reference repositories can be watched for their latest stable GitHub release. Their release tag, date, URL, body hash, and bounded body excerpt are evidence only; they are never installed or imported as skills automatically.

### REQ-007
**Durable local evidence.**

Remote checks write a versioned summary under `$LAI_DATA_DIR/update-intelligence`, compare against the previous observation, and keep public source checkout HEAD/status invariant.

### REQ-008
**No automatic mutation.**

The command exposes no apply/install/download/update/PR/commit/push/merge/tag/publish operation and never calls the model. A candidate update must enter the normal spec, workspace, validation, review, and protected-main flow separately.
## Acceptance Criteria

- `lai update plan --json` works with no model/server/network.
- `lai update check` without `--remote` refuses network execution clearly.
- Remote fetching rejects unsupported hosts/schemes and oversized or non-JSON responses.
- Exact dev pins and Harness Score current versions are parsed from canonical repository files.
- llama.cpp build evidence comes from authenticated local props or is explicitly unknown.
- PyPI current-version vulnerability entries are surfaced without executing package-manager commands.
- Reference upstream release bodies are bounded and hashed.
- Repeated checks report whether each upstream changed since the prior observation.
- Results remain under LAI data state with bounded retention; source HEAD/status are invariant.
- Full validation/publication gates stay green.

## Implementation Notes

- Keep the source manifest versioned in `updates/sources-v1.json` and synchronize it into installed LAI data state.
- Use fixed source-type handlers rather than generic fetch or caller-provided URLs.
- Persist summaries atomically outside the source checkout and retain only a bounded recent history.
- Treat incompatible version schemes as manual compatibility-review evidence.
- Explicitly lint the extensionless `src/local-agent` so the main runtime cannot evade Ruff discovery.

## Non-Goals

- Automatic dependency/skill/model installation.
- Generic web search or arbitrary URL fetch.
- Automatic PRs, merges, releases, or model-driven update decisions.
- Trusting third-party skill registries by default.
- Replacing Dependabot where it already provides the safer mechanism.
## Traceability

- `REQ-001` -> `updates/sources-v1.json`, manifest validation, installed-manifest smoke.
- `REQ-002` -> offline plan renderer and no-network regression.
- `REQ-003` -> bounded trusted-host HTTP helper and network-boundary tests.
- `REQ-004` -> repository pin parsing and authenticated llama props detector.
- `REQ-005` -> version classifier, PyPI vulnerability classifier, and focused tests.
- `REQ-006` -> GitHub stable-release watcher and bounded release evidence tests.
- `REQ-007` -> `$LAI_DATA_DIR/update-intelligence` persistence, retention, change detection, and source-invariance tests.
- `REQ-008` -> CLI surface tests plus full policy/publication regressions.

## Validation

- `REQ-001`: manifest validation, canonical-pin consistency, install smoke.
- `REQ-002`: offline plan/no-network regression.
- `REQ-003`: scheme/host/redirect/credential/size/JSON boundary regressions.
- `REQ-004`: canonical pin and llama build detector regressions.
- `REQ-005`: version classification and exact-version PyPI vulnerability regression.
- `REQ-006`: canonical GitHub release URL, bounded excerpt, and untrusted-content regression.
- `REQ-007`: persistence, latest, changed-since-last-check, retention, and source-invariance regressions.
- `REQ-008`: forbidden CLI verbs plus full publication/policy gates.
- Full gates: `make lint`, `make typecheck`, `make check`, `make test-dev`, `make test`, `make harness-score-gate`, `make validate`.

## Validation Evidence

- Focused update-intelligence regressions: 13 passed.
- Installed-copy smoke: canonical update manifest installed and `lai update plan --json` works outside the source checkout.
- Live dogfood: two explicit remote checks succeeded; the second reported unchanged observations and preserved source HEAD/status.
- Full pytest: 238 passed + 85 subtests.
- Full unittest: 238 passed.
- Ruff includes the extensionless `src/local-agent`; strict mypy and static checks are green.
- Harness maturity no-regression gate: L4, 100/108 (93%).
- Publication scan and VSIX inspection are green.
- First live candidate: Harness Score 1.6.4 observed over pinned 1.6.3; no update was applied in this cut.
