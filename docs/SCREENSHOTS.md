# Screenshots

These assets are generated from real local CLI output and sanitized for public documentation. They do not include tokens, private paths, raw logs or customer data.

| Asset | Source command | Notes |
| --- | --- | --- |
| [lai help](assets/screenshots/lai-help.svg) | `./src/lai --help` | Top-level CLI surface. |
| [readiness](assets/screenshots/lai-readiness.svg) | `./src/lai readiness --json` | Local readiness diagnostic; paths sanitized. |
| [validation matrix](assets/screenshots/lai-validation-matrix.svg) | `./src/lai validation matrix` | Risk-proportional validation overview. |
| [distribution status](assets/screenshots/lai-distribution-status.svg) | `LAI_DATA_DIR=<fixture> ./src/lai distribution status` | Isolated fixture to avoid exposing local state. |

Gateway UI screenshots are intentionally not included in this repository graduation pass because the companion Gateway UI is separate and was not safely executed in this checkout. Browser, MCP and external-action screenshots are also omitted because current implementations are fixture/control-plane contracts rather than user-facing real integrations.
