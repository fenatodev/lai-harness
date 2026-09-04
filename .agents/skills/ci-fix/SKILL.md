---
name: ci-fix
description: Use when fixing a concrete failing check, test, lint, package, or publication gate while preserving the real failure signal.
---

MODE: CI-FIX
Goal: fix the smallest verified cause of a failing local or CI validation.

Workflow:
1. Read the failing command, error, log, or gate output first.
2. Inspect the directly implicated code, test, workflow, script, or package metadata.
3. Patch only the proven cause.
4. Run the closest local equivalent of the failing validation.
5. Stop for explicit human Git release actions instead of tagging, merging, or pushing.

Evidence rules:
- Never mask a failing test, weaken assertions, or skip checks unless the user explicitly requested that exact change and the rationale is grounded.
- Do not edit unrelated files.
- Do not claim CI is fixed unless a real validation command passed locally or the limitation is stated.

Final exactly:
Causa: <validated cause>
Correção: <small diff summary>
Validação: <command and result>
Próximo passo: <human release/CI action if needed>

Maximum 120 words.
