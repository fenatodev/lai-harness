---
description: Release rules for versioning, packaging, installation, publication, and Git-facing changes.
globs:
  - "CHANGELOG.md"
  - "README*.md"
  - "docs/**"
  - "scripts/**"
  - "vscode-extension/**"
---

# Release and Publication

- Keep release metadata consistent across core, tests, extension, documentation, and changelog.
- Run the complete publication gate before installation or tagging.
- Never install modified source before validation is green.
- Verify installed/source hashes after replacing the executable.
- Verify version and doctor/readiness after installation.
- Do not automatically create commits, tags, merges, or pushes.
- Preserve compatibility intentionally.
- Never perform broad identity renames with blind global replacement.
