# Security Policy

The current shipped boundary is documented in [Security model](docs/SECURITY-MODEL.md), [Threat model](docs/AUTONOMY-THREAT-MODEL.md), [Authority and approvals](docs/AUTHORITY-APPROVALS.md), [Sandbox](docs/SANDBOX.md), and [Known limitations](docs/KNOWN-LIMITATIONS.md).

## Reporting vulnerabilities

Do not open a public issue for a suspected vulnerability. Use GitHub private vulnerability reporting for this repository when available. Include:

- affected version or commit;
- trust boundary involved;
- minimal synthetic reproduction;
- expected and actual behavior;
- impact;
- proposed mitigation if known.

Do not include real keys, private repositories, customer data, raw handoffs, local runtime state, model files, audit logs, prompts or proprietary source.

## Supported versions

The current public package reports `lai harness 0.5.0`. After a stable release line is published, the latest published `0.5.x` patch line receives security fixes. Pre-release or local-only builds are supported only when explicitly identified as the active test line.

## Current security posture

Implemented:

- authenticated loopback control plane;
- local-chat Host/Origin/CSRF checks;
- path confinement and symlink escape protection;
- safe workspaces and hash-bound promotion;
- verified sandbox executor for remote work-runs when the required local Docker image is present;
- metadata-only trajectory, event and public record views;
- fake credential and fake external-action adapters only;
- governed, bounded, untrusted web evidence;
- fixture-only browser and MCP execution.

Not implemented:

- real credential use;
- real GitHub/account effects;
- real browser profile or login automation;
- generic MCP tool execution;
- trusted-host and computer-use A10/A11 profiles.

## Operational warning

`lai harness` is a developer tool, not a complete security sandbox. Run it with least privilege, keep backups, protect credentials, inspect diffs and validation output, and keep model/control endpoints bound to loopback unless a separate reviewed boundary exists.
