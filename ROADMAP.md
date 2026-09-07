# Roadmap

## Near term

- Treat `v0.4.5` plus `lai-gateway` `v0.1.31` as the current stable integration baseline. Do not expand remote authority until rollback, trust, and context quality improve.
- `v0.4.6` stability focus: keep recovery/checkpoint state inspectable and harden hash-checked rollback with installed dogfood evidence, without using `git reset` or replaying tool calls.
- Next after recovery: improve token-efficient context intelligence through structured repo maps, symbol summaries, and compact diff/test/process views.
- Continue incremental subsystem extraction from `src/local-agent` only when a tested runtime slice is ready; no Big Bang modular rewrite.
- Keep update-evidence convergence under dogfood across stable upgrades; add automation only when repeated evidence proves it saves more time than it costs.
- Expand automated model-evaluation fixtures from observed dogfood failures and keep Ministral as the baseline until repeated decision-eligible evidence beats it.
- Keep generic `bash` out of remote control profiles; evolve structured `validate`/sandbox capabilities from measured fixtures rather than exposing shell text.
- Keep repository-scoped sessions, read-only web evidence, and the non-executing MCP broker under dogfood; expand them only from measured failures and without enabling broad MCP/browser authority.

## Adjacent projects

- `lai-gateway` (separate repository): Telegram first, then a private PWA through Tailscale; it consumes `lai serve` rather than embedding messaging credentials in the harness.
- Commercial automation companion (separate product/repository): CRM, lead capture, social inbox/content, follow-up, scheduling and reactivation. Use lai harness to build and dogfood it instead of merging business automation into the coding harness.

## Later

- Support multiple OpenAI-compatible local providers without provider-specific prompts.
- Add more focused mode skills only after they prove distinct from diagnose, ci-fix, release, and existing modes.
- Add interactive approval UI and scoped approval grants for `ASK` operations.
- Add gateway approval UX for promotion, then guarded commit/push/PR actions on promoted feature worktrees.
- Evolve persistent-session lifecycle, explicit deletion, compaction quality, and gateway-side user/session mapping after real mobile dogfood.
- Evolve read-only web evidence from dogfood before considering any stateful/browser-action capability.
- Evolve the MCP broker from non-executing config discovery into allowlisted tool execution under the same policy layer.
- Add deterministic wave orchestration for subagents/delegates using explicit dependencies and disjoint file ownership.
- Add quality-gate ratchets: measure as warning, enforce no-regression, then promote to required gate when debt reaches zero.
- Add token-efficient structured views for Git, tests, diffs, process state, and other verbose evidence.
- Keep the Ministral baseline until another <=8 GiB candidate beats it with repeated, decision-eligible local model-evaluation evidence; Qwen dogfood did not clear that bar for the current milestone.
- Explore signed releases and provenance attestations.

Roadmap items are intentions, not commitments. Model redistribution and automatic downloading are deliberately out of scope.

- v0.4.0: first stable core with protected release governance, bounded remote work/promotion, typed runtime-module ratchets, update intelligence, repeated model evaluation, and a finite stable-readiness gate.
- v0.4.0-alpha.20: sanitized run export bundle with `lai run export`.
- v0.4.0-alpha.21: release preflight and public mode aliases before beta readiness.
- v0.4.0-beta.1: first beta readiness cut with deterministic release gates and documented stabilization posture.
- v0.4.0-beta.2: release polish with current GitHub metadata, release notes, checklist, and public VSIX artifact naming.
- v0.4.0-beta.24: first typed runtime-module extraction for semantic code contracts, installed-runtime compatibility, and an expanded strict mypy ratchet.
- v0.4.0-beta.23: stale update-evidence convergence across local baseline changes, with explicit refresh and stale-action suppression.
- v0.4.0-beta.22: offline update triage with security-first prioritization plus the first governed radar-driven dependency refresh.
- v0.4.0-beta.21: bounded update intelligence for trusted dependencies/runtime metadata and reference-agent release observation, with no automatic apply path.
- v0.4.0-beta.20: automated local model evaluation with disposable fixtures, independent validation, provenance, repeated sampling, and decision eligibility.
- v0.4.0-beta.19: target-version-bound release metadata generation and stale-release-note prevention.
- v0.4.0-beta.18: versioned runtime-record schemas plus configurable bounded state/metrics/audit retention.
- v0.4.0-beta.17: Node 24 GitHub Actions supply-chain hardening with reviewed full-SHA pins and Dependabot updates.
- v0.4.0-beta.16: reproducible development quality sensors with a generated pinned lock, strict mypy guardrail ratchet, and CI/publication enforcement.
- v0.4.0-beta.15: SHA-256-bound approved promotion from successful isolated work into dedicated `lai/promotion-*` Git worktrees, with repeated sandbox validation and source-drift checks.
- v0.4.0-beta.14: isolated remote work runs with disposable safe workspaces, structured validation, Docker sandboxing, and bounded diff evidence.
- v0.4.0-beta.13: explicit shell-free remote capability profiles with read-only `diagnose` and `release` control runs.
- v0.4.0-beta.12: serialized asynchronous `plan`/`review`/`security` control runs with bounded lifecycle, output, queueing, and cancellation.
- v0.4.0-beta.11: authenticated loopback local control plane foundation for future mobile gateways.
- v0.4.0-beta.10: release-state convergence with remote-aware handoff and tag-safe main integration evidence.
- v0.4.0-beta.9: self-correcting development harness with policy-backed hooks and an L4 maturity CI ratchet.
- v0.4.0-beta.8: opt-in remote GitHub release governance with protected-main and pre-release verification.
- v0.4.0-beta.7: project handoff command and next-chat reference files for long-session migration.
- v0.4.0-beta.6: release governance status for local readiness, release-pack state, and manual GitHub publication actions.
- v0.4.0-beta.5: release publication pack for local GitHub Release body, checklist, summary and optional VSIX generation.
- v0.4.0-beta.4: safe workspace dogfood commands for disposable local testing away from protected branches.
- v0.4.0-beta.3: protected branch write guard for safer local smoke testing and release inspection.
