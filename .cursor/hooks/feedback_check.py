#!/usr/bin/env python3
"""Best-effort, repository-confined feedback for files edited by an agent."""

import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def edited_path(payload):
    if not isinstance(payload, dict):
        return None
    value = payload.get("file_path") or payload.get("filePath")
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    try:
        resolved = candidate.resolve()
        resolved.relative_to(ROOT.resolve())
    except (OSError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def run(command):
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=6,
        check=False,
    )


def feedback_commands(path):
    rel = path.relative_to(ROOT).as_posix()
    if path.suffix == ".py" or rel == "src/local-agent":
        commands = [[sys.executable, "-m", "py_compile", str(path)]]
        ruff = ROOT / ".venv" / "bin" / "ruff"
        if path.suffix == ".py" and ruff.is_file():
            commands.insert(0, [str(ruff), "format", str(path)])
            commands.append([str(ruff), "check", str(path)])
        return commands
    if path.suffix in {".js", ".mjs", ".cjs"}:
        node = shutil.which("node")
        return [[node, "--check", str(path)]] if node else []
    if path.suffix == ".json":
        return [[sys.executable, "-m", "json.tool", str(path)]]
    if path.suffix == ".sh" or rel == "src/lai":
        bash = shutil.which("bash")
        return [[bash, "-n", str(path)]] if bash else []
    return []


def main():
    diagnostics = []
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        path = edited_path(payload)
        if path:
            for command in feedback_commands(path):
                result = run(command)
                if result.returncode != 0:
                    detail = (result.stderr or result.stdout).strip().splitlines()
                    diagnostics.append(detail[0] if detail else "feedback check failed")
    except Exception as exc:
        diagnostics.append(f"feedback hook skipped: {exc}")

    if diagnostics:
        sys.stderr.write("lai feedback: " + " | ".join(diagnostics[:3]) + "\n")
    sys.stdout.write("{}")


if __name__ == "__main__":
    main()
