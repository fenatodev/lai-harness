# LAI — Local AI Agent for VS Code

This extension connects the `@lai` chat participant to a separately installed `local-agent` harness. It does not contain a model, model server, API key, workspace state, or audit data.

Install the harness from the repository root first. The default executable is `~/.local/bin/local-agent`; set `lai.agentPath` to an absolute path when using an isolated or non-default installation.

See the repository README and security model before using write-capable modes. LAI's guarded shell execution is not a sandbox.
