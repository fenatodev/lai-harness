# Skills

Skills provide mode-specific instructions and diagnostics. They are not authority.

## Locations

| Location | Purpose |
| --- | --- |
| `.agents/skills/<mode>/SKILL.md` | Standard portable skill format. |
| `skills/<mode>.txt` | Legacy compatibility fallback. |

## Standard skill contract

A standard `SKILL.md` requires `name` and `description`. Optional fields may declare `schema_version`, `version`, `provenance`, `context`, `capabilities`, `tools`, `validation` and `outputs`.

The loader reports missing tools, missing capabilities, unknown metadata fields, authority claims and body hash. Future schema versions fail closed.

## Authority boundary

Skill declarations:

- cannot install packages;
- cannot execute hooks at load time;
- cannot read secrets;
- cannot grant approvals;
- cannot rewrite policy;
- cannot add tools beyond the fixed mode profile.

They may guide the model, but deterministic safety gates still decide what can execute.
