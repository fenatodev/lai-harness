# Security Policy

## Reporting

Do not open a public issue for a suspected vulnerability. Use GitHub's private vulnerability reporting for this repository when available. Include the affected version, trust boundary, reproduction with synthetic data, impact, and proposed mitigation.

## Supported versions

After the first stable release, the latest published `0.4.x` patch line receives security fixes. Pre-release builds are supported only when explicitly identified as the active test line.

## Operational warning

LAI is a developer tool, not a security sandbox. Its shell tool runs with the launching user's permissions. Use least privilege, isolate valuable credentials, keep backups, inspect changes, and never expose the model server without authentication and network controls.
