# Security Policy

## Reporting

Do not open a public issue for a suspected vulnerability. Use GitHub's private vulnerability reporting for this repository when available. Include the affected version, trust boundary, reproduction with synthetic data, impact, and proposed mitigation.

## Supported versions

Until the project reaches a stable release, only the latest published minor version receives security fixes.

## Operational warning

LAI is an experimental developer tool, not a security sandbox. Its shell tool runs with the launching user's permissions. Use least privilege, isolate valuable credentials, keep backups, inspect changes, and never expose the model server without authentication and network controls.
