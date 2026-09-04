# Spec: GitHub project presentation

## Metadata
- Mode: `quick`
- Status: `complete`

## Goal
Present lai harness on GitHub as a professional, current engineering product without weakening technical accuracy or release governance.

## Requirements
- REQ-001: Version the three approved architecture diagrams under stable `docs/assets/` names and use them in appropriate README/docs surfaces.
- REQ-002: Rework README hierarchy so product identity, current beta status, core differentiators, quick start, architecture, security and release discipline are immediately discoverable.
- REQ-003: Keep English and Portuguese README surfaces aligned on current version and primary capabilities.
- REQ-004: Add a version-coupled visual-asset review marker and automated test so every product version bump requires explicit diagram review.
- REQ-005: Update GitHub-facing metadata guidance (description/topics) and release checklist so future releases review presentation assets when architecture changes.
- REQ-006: Preserve existing public claims: local `bash` is unsandboxed; remote control profiles are shell-free/write-free; gateway/Tailscale is a companion architecture and not part of the core harness runtime.

## Acceptance Criteria
- README renders the core architecture image and points to release/mobile architecture docs without broken relative links.
- Publication/version tests pass with the visual asset review marker.
- No credentials, machine-specific private paths, or private-project names are added.
- Full publication validation remains green.

## Non-Goals
- No runtime behavior change.
- No version bump.
- No new GitHub release.
- No claim that the companion gateway is already part of the lai-harness distribution.
