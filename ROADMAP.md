# Roadmap

## Near term

- Extend semantic code contracts as subsystems split out of `src/local-agent`.
- Extend the model-evaluation harness with automated run capture and hardware profiles.
- Harden the `ALLOW` / `ASK` / `DENY` policy with structured commands or a stronger execution boundary.
- Expand end-to-end fixtures for every mode and guard.
- Add JSON schemas and configurable retention for state, metrics, and audit events.
- Stabilize the loopback control plane, then design asynchronous agent runs and explicit `ASK` approval objects before enabling write-capable mobile operation.

## Adjacent projects

- `lai-gateway` (separate repository): Telegram first, then a private PWA through Tailscale; it consumes `lai serve` rather than embedding messaging credentials in the harness.
- Commercial automation companion (separate product/repository): CRM, lead capture, social inbox/content, follow-up, scheduling and reactivation. Use lai harness to build and dogfood it instead of merging business automation into the coding harness.

## Later

- Support multiple OpenAI-compatible local providers without provider-specific prompts.
- Add more focused mode skills only after they prove distinct from diagnose, ci-fix, release, and existing modes.
- Add interactive approval UI and scoped approval grants for `ASK` operations.
- Provide an optional containerized/disposable executor.
- Use model-evaluation data to decide whether Qwen Coder or another <=8 GB model should replace the current baseline.
- Explore signed releases and provenance attestations.

Roadmap items are intentions, not commitments. Model redistribution and automatic downloading are deliberately out of scope.

- v0.4.0-alpha.20: sanitized run export bundle with `lai run export`.
- v0.4.0-alpha.21: release preflight and public mode aliases before beta readiness.
- v0.4.0-beta.1: first beta readiness cut with deterministic release gates and documented stabilization posture.
- v0.4.0-beta.2: release polish with current GitHub metadata, release notes, checklist, and public VSIX artifact naming.
- v0.4.0-beta.11: authenticated loopback local control plane foundation for future mobile gateways.
- v0.4.0-beta.10: release-state convergence with remote-aware handoff and tag-safe main integration evidence.
- v0.4.0-beta.9: self-correcting development harness with policy-backed hooks and an L4 maturity CI ratchet.
- v0.4.0-beta.8: opt-in remote GitHub release governance with protected-main and pre-release verification.
- v0.4.0-beta.7: project handoff command and next-chat reference files for long-session migration.
- v0.4.0-beta.6: release governance status for local readiness, release-pack state, and manual GitHub publication actions.
- v0.4.0-beta.5: release publication pack for local GitHub Release body, checklist, summary and optional VSIX generation.
- v0.4.0-beta.4: safe workspace dogfood commands for disposable local testing away from protected branches.
- v0.4.0-beta.3: protected branch write guard for safer local smoke testing and release inspection.
