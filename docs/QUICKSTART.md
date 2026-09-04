# Quick start

1. Install and configure LAI using [Installation](INSTALLATION.md).
2. Start your authenticated `llama.cpp` endpoint directly or run `scripts/ministral-start` after configuring its Windows launcher.
3. Run `lai doctor`.
4. Open a trusted Git repository in VS Code and reload the extension host.
5. Address the participant as `@lai`.

Examples:

```text
@lai /plan add input validation without changing the public API
@lai /debug reproduce the failing timeout test and trace the exact value
@lai /implement add the requested regression test and smallest fix
@lai /review review my current Git diff
@lai /security trace untrusted input to sensitive operations
@lai /status
@lai /metrics
@lai /audit
lai spec
lai context "repair parser timeout"
lai recovery
# only when recovery reports a compatible interrupted run:
lai resume
@lai /handoff Ready for a high-context architecture review
```

Run `/plan`, `/debug`, `/review`, or `/security` when you want read-only analysis. Write-capable modes still operate with your user permissions: inspect the Git diff and run the repository's required checks before accepting work.
