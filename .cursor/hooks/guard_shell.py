#!/usr/bin/env python3
"""Cursor shell gate backed by lai harness's deterministic policy engine."""

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "src" / "local-agent"


def emit(permission: str, message: str | None = None) -> None:
    payload: dict[str, str] = {"permission": permission}
    if message:
        payload["userMessage"] = message[:500]
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))


def extract_command(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    command = payload.get("command")
    if isinstance(command, str) and command.strip():
        return command
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str) and command.strip():
            return command
    return None


def classify(command: str) -> dict[str, str]:
    request = {
        "tool": "bash",
        "args": {"command": command},
        "mode": "unknown",
    }
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    proc = subprocess.run(
        [sys.executable, str(POLICY), "--policy-check", "--stdin", "--json"],
        cwd=ROOT,
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=4,
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "policy-check failed")
    result = json.loads(proc.stdout)
    if not isinstance(result, dict):
        raise RuntimeError("invalid policy-check result")
    decision = result.get("decision")
    if not isinstance(decision, str) or decision not in {"ALLOW", "ASK", "DENY"}:
        raise RuntimeError("invalid policy-check result")
    reason = result.get("reason")
    reason_text = reason if isinstance(reason, str) and reason else "policy decision has no reason"
    return {"decision": decision, "reason": reason_text}


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        command = extract_command(payload)
        if not command:
            emit("ask", "lai shell gate could not identify the command; explicit review required.")
            return
        result = classify(command)
    except Exception as exc:
        emit("ask", f"lai shell gate failed closed: {exc}")
        return

    decision = result["decision"]
    reason = result["reason"]
    if decision == "DENY":
        emit("deny", f"Blocked by lai policy: {reason}")
    elif decision == "ASK":
        emit("ask", f"lai policy requires explicit user action: {reason}")
    else:
        emit("allow")


if __name__ == "__main__":
    main()
