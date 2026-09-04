---
name: release
description: Use when checking whether a version can be released, preparing release notes, or producing safe human-only release commands.
---

MODE: RELEASE
Goal: verify release readiness and produce exact human-run commands without performing sensitive Git mutations.

Workflow:
1. Start from the preloaded RELEASE PREFLIGHT. Treat it as read-only repository evidence.
2. Inspect only missing release evidence: version consistency, spec status, docs, tests, and Git state.
3. Prefer repository-defined commands from the preflight, especially `make check` and `make validate`.
4. Identify blockers before suggesting release commands.
5. Produce tag/merge/push commands only as instructions for the user.

Evidence rules:
- Do not edit files.
- Do not run git tag, merge, push, release publication, or package upload.
- Do not probe ad-hoc pytest/python commands when Makefile or script commands are available.
- Do not declare a release ready unless repository evidence and validations support it.
- Mention unsigned tags as normal unless the project requires signing.

Final exactly:
Status: <ready | blocked>
Evidência: <checks inspected>
Bloqueios: <none or concrete blockers>
Comandos humanos: <exact commands or none>

Maximum 150 words.
