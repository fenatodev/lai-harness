---
description: Rules for portable agent skills, progressive disclosure, trust, and legacy skill compatibility.
globs:
  - "skills/**"
  - ".agents/skills/**"
  - "src/**"
---

# Skills

- Standard skills use a `SKILL.md` file with validated metadata.
- Skill descriptions must state clearly when the skill should activate.
- Prefer progressive disclosure: metadata first, full instructions only when selected.
- Do not load every skill body into every prompt.
- Preserve legacy `skills/<mode>.txt` compatibility until migration is complete.
- Repository or remote skills are not automatically trusted executable policy.
- Skills may guide the model but cannot override deterministic safety gates.
