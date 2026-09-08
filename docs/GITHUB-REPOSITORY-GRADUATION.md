# GitHub repository graduation notes

This checklist records public-repository readiness items after A12 documentation graduation. It does not perform remote GitHub actions.

## Local repository assets

| Item | Status | Notes |
| --- | --- | --- |
| README | Updated | English and Portuguese READMEs describe implemented post-A12 behavior. |
| License | Present | MIT license. |
| Security policy | Present | Updated to current boundaries. |
| Contributing guide | Updated | Explains clone, setup, specs, tests and safety constraints. |
| Code of Conduct | Present | Lightweight contributor conduct policy. |
| Issue templates | Present | Bug and feature templates use synthetic data. |
| Pull request template | Updated | Uses risk-proportional validation and privacy checks. |
| GitHub Actions | Present | CI, publication and Harness Score workflows remain local files only. |
| Dependabot | Present | Existing `.github/dependabot.yml`. |
| Visual assets | Present | Existing PNG assets plus post-A12 SVG diagrams and CLI screenshots. |
| Changelog | Updated | Unreleased section references documentation graduation. |

## Suggested GitHub description

`Local-first, auditable coding harness for OpenAI-compatible local LLM servers.`

## Suggested topics

`local-first`, `llm`, `coding-agent`, `developer-tools`, `openai-compatible`, `python`, `vscode`, `sandbox`, `security`, `agent-harness`, `local-llm`, `control-plane`.

## Manual actions not performed

- Commit, branch, tag, merge or push.
- GitHub release creation.
- Marketplace/VSIX publication.
- Branch protection or required-check changes.
- Repository description/topics/social preview updates.
- Secrets, environments or remote settings changes.

## Social preview/banner

No new social preview is configured remotely. The safest current visual source is `docs/assets/core-architecture.png` plus the SVG diagrams under `docs/assets/diagrams/`. A maintainer can choose a social preview manually after reviewing rendered output on GitHub.
