# Update intelligence

`lai update` is a read-only maintenance radar for lai harness. It helps an operator discover relevant upstream changes without turning release metadata or package registries into an execution channel.

## Commands

```bash
lai update plan
lai update plan --json
lai update check --remote
lai update check --remote --json
lai update latest
lai update latest --json
```

`plan` is deterministic and offline. `check` requires the explicit `--remote` flag. `latest` reads only the most recent local observation.

There is intentionally no `apply`, `install`, `download`, `upgrade`, `commit`, `push`, `merge`, or release-publication operation.

## Trust boundary

Tracked sources are enumerated in `updates/sources-v1.json`. Callers and models cannot provide arbitrary fetch URLs.

Remote metadata is limited to fixed official hosts and bounded HTTPS GET requests. Redirects are disabled, credentials are not attached to public update feeds, response size/time are bounded, and JSON is required.

Release-note bodies from upstream projects are **untrusted evidence**. lai stores only a bounded excerpt plus SHA-256 provenance. That text is never executed or treated as model/system instructions.

Reference agents such as Codex, Claude Code, Qwen Code, Kimi Code, and Hermes Agent are watched for engineering ideas only. They are not dependencies and their skills are never imported automatically.

## Dependency posture

Python development sensors are compared against exact repository pins. PyPI-backed sources also expose vulnerability metadata for the exact pinned version when available from the official API.
GitHub Actions remain managed by Dependabot rather than duplicated by a second updater. Harness Score is observed as a pinned development tool.

The active llama.cpp runtime build is read from authenticated local `/props` when available. Build identifiers such as `b10730` are not compared numerically with release tags such as `v0.4.0`; incompatible version schemes produce a manual compatibility-review signal instead of a fake upgrade recommendation.

## Durable evidence

Remote checks write versioned JSON under `$LAI_DATA_DIR/update-intelligence/` and update `latest.json` atomically. Each source records current/latest identifiers, status, security posture, provenance, and whether the observation changed since the previous check.

The active repository HEAD/status is sampled before and after every remote check. Any observed mutation aborts the check.

## Update workflow

A detected update is evidence for a separate governed change:

1. inspect the upstream delta and security impact;
2. create a focused spec/feature branch;
3. update only the required pins/configuration;
4. validate in the normal harness gates and dogfood where relevant;
5. integrate through protected `main` and release governance.
