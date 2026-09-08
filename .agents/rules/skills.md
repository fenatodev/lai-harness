---
description: Rules for portable agent skills, progressive disclosure, trust, and legacy skill compatibility.
globs:
  - "skills/**"
  - ".agents/skills/**"
  - "src/**"
---

# Skills

- Standard skills use a `SKILL.md` file with validated frontmatter. Required fields remain `name` and `description`; optional fields may declare `schema_version`, `version`, `provenance`, `context`, `capabilities`, `tools`, `validation`, and `outputs`.
- Skill descriptions must state clearly when the skill should activate.
- Prefer progressive disclosure: metadata first, full instructions only when selected.
- Do not load every skill body into every prompt.
- Preserve legacy `skills/<mode>.txt` compatibility until migration is complete.
- Repository or remote skills are not automatically trusted executable policy.
- Skill declarations are diagnostics, not authority. They cannot install packages, execute hooks, read secrets, grant approvals, rewrite policy, or add tools beyond the fixed mode profile.
- Future `schema_version` values fail closed until the harness explicitly supports them.
- Skills may guide the model but cannot override deterministic safety gates.
