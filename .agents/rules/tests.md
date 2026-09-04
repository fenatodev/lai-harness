---
description: Testing and regression rules for changes affecting lai harness source behavior or fixtures.
globs:
  - "tests/**"
  - "src/**"
---

# Tests and Validation

- Prefer focused regression tests for the exact behavior being changed.
- Never weaken assertions solely to make faulty source code pass.
- Repair source first after assertion regressions unless evidence proves the test is wrong.
- Run focused tests before the full suite.
- Do not describe narrow checks as broader proof.
- Keep fake-server and integration fixtures deterministic and bounded.
- Redirect potentially verbose test output to temporary logs when practical.
