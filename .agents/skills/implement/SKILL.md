---
name: implement
description: Use when implementing explicit acceptance criteria with minimal changes and mandatory validation.
---

MODE: IMPLEMENT
Goal: complete every explicit acceptance criterion with the smallest coherent patch and validate it.

A project snapshot may already provide exact paths and scripts.

Workflow:
1. Identify every explicit acceptance criterion.
2. Inspect AGENTS.md and all known relevant implementation/test files together in ONE inspect call whenever possible.
3. Search only if a required path or symbol is unknown. Never guess paths.
4. Apply related existing-file replacements in ONE patch call whenever possible.
5. Create files only when genuinely required.
6. After the final modification, run the narrowest required validation.

Rules:
- Requested tests are mandatory.
- Never repeat a stale patch.
- Never install dependencies.
- Never refactor unrelated code.
- Never conclude with incomplete criteria.
- Never conclude with unvalidated changes.
- Do not commit or push.

Final:
Implemented: <complete change>
Files: <changed files>
Validation: <command/result/what it proves>
Uncertainty: <meaningful uncertainty or "none">

Maximum 120 words.

Post-patch sanity:
- The harness may run a compact diff-only defect check after patch.
- If POST_PATCH_SANITY reports a BUG, fix that concrete defect before validation/conclusion.
- Do not argue with or ignore a concrete sanity finding.
- A CLEAN sanity result does not replace the required project validation.

Deterministic sanity:
- After patch, the harness may run language syntax checks and added-line static checks before the diff classifier.
- A static BUG is concrete evidence and must be corrected before validation/conclusion.
- Project tests remain mandatory even after static sanity passes.
