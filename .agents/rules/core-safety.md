---
description: Core safety invariants for lai harness runtime, tools, policy, and executable scripts.
globs:
  - "src/**"
  - "scripts/**"
---

# Core Safety

- Preserve repository confinement and symlink protections.
- Preserve deterministic post-write validation.
- Preserve fail-closed behavior for critical safety decisions.
- Do not replace deterministic gates with prompt-only instructions.
- Do not silently broaden filesystem, shell, Git, network, or external-write capabilities.
- Future MCP and plugin actions must use the same policy boundary as builtin tools.
- Do not install dependencies from autonomous execution paths.
- Keep runtime changes narrow and auditable.
