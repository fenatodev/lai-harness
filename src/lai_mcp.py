from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

MCP_CONFIG_CANDIDATES = (
    Path(".cursor/mcp.json"),
    Path(".mcp.json"),
    Path(".agents/mcp_config.json"),
)

_CREDENTIAL_KEY_RE = re.compile(
    r"(api[_-]?key|token|secret|password|passwd|credential|auth)",
    re.IGNORECASE,
)
_ENV_INTERPOLATION_RE = re.compile(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}")


@dataclass(frozen=True)
class McpConfigIssue:
    severity: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"severity": self.severity, "path": self.path, "message": self.message}


def _repo_relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        if _ENV_INTERPOLATION_RE.search(value):
            return value
        if _CREDENTIAL_KEY_RE.search(value) or len(value) >= 20:
            return "<redacted>"
        return value
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _redact_value(v) for k, v in value.items()}
    return value


def _looks_credential_key(key: object) -> bool:
    return isinstance(key, str) and bool(_CREDENTIAL_KEY_RE.search(key))


def _uses_env_interpolation(value: object) -> bool:
    return isinstance(value, str) and bool(_ENV_INTERPOLATION_RE.search(value))


def _server_map(data: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in ("mcpServers", "servers"):
        value = data.get(key)
        if isinstance(value, Mapping):
            return value
    return {}


def discover_mcp_config(root: Path) -> dict[str, Any]:
    root = root.resolve()
    configs: list[dict[str, Any]] = []
    servers: list[dict[str, Any]] = []
    issues: list[McpConfigIssue] = []

    for rel in MCP_CONFIG_CANDIDATES:
        path = root / rel
        if not path.exists():
            continue
        public_path = _repo_relative(root, path)
        if path.is_symlink():
            issues.append(McpConfigIssue("error", public_path, "MCP config must not be a symlink"))
            configs.append({"path": public_path, "status": "blocked", "server_count": 0})
            continue
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            issues.append(McpConfigIssue("error", public_path, f"invalid JSON: {exc}"))
            configs.append({"path": public_path, "status": "blocked", "server_count": 0})
            continue
        if not isinstance(data, Mapping):
            issues.append(McpConfigIssue("error", public_path, "MCP config root must be a JSON object"))
            configs.append({"path": public_path, "status": "blocked", "server_count": 0})
            continue
        server_map = _server_map(data)
        configs.append({"path": public_path, "status": "loaded", "server_count": len(server_map)})
        if not server_map:
            issues.append(McpConfigIssue("warning", public_path, "no MCP servers declared"))
            continue
        for name, server in sorted(server_map.items(), key=lambda item: str(item[0])):
            public_server_path = f"{public_path}:{name}"
            if not isinstance(name, str) or not name.strip():
                issues.append(McpConfigIssue("error", public_server_path, "server name must be a non-empty string"))
                continue
            if not isinstance(server, Mapping):
                issues.append(McpConfigIssue("error", public_server_path, "server definition must be a JSON object"))
                continue
            command = server.get("command")
            args = server.get("args", [])
            env = server.get("env", {})
            if not isinstance(command, str) or not command.strip():
                issues.append(McpConfigIssue("error", public_server_path, "server command must be a non-empty string"))
            if args is not None and not (
                isinstance(args, list) and all(isinstance(item, str) for item in args)
            ):
                issues.append(McpConfigIssue("error", public_server_path, "server args must be a list of strings"))
                args = []
            if env is None:
                env = {}
            if not isinstance(env, Mapping):
                issues.append(McpConfigIssue("error", public_server_path, "server env must be a JSON object"))
                env = {}
            credential_env_keys: list[str] = []
            unsafe_env_keys: list[str] = []
            for key, value in sorted(env.items(), key=lambda item: str(item[0])):
                if not isinstance(key, str) or not key.strip():
                    issues.append(McpConfigIssue("error", public_server_path, "env keys must be non-empty strings"))
                    continue
                if _looks_credential_key(key):
                    credential_env_keys.append(key)
                    if not _uses_env_interpolation(value):
                        unsafe_env_keys.append(key)
                        issues.append(
                            McpConfigIssue(
                                "error",
                                f"{public_server_path}.env.{key}",
                                "credential-shaped env values must use ${ENV_VAR} interpolation",
                            )
                        )
            servers.append(
                {
                    "name": name,
                    "config_path": public_path,
                    "command": command if isinstance(command, str) else None,
                    "args": _redact_value(args if isinstance(args, list) else []),
                    "args_count": len(args) if isinstance(args, list) else 0,
                    "env_keys": sorted(str(key) for key in env.keys() if isinstance(key, str)),
                    "credential_env_keys": credential_env_keys,
                    "unsafe_env_keys": unsafe_env_keys,
                    "status": "blocked" if unsafe_env_keys else "declared",
                }
            )

    if not configs:
        overall = "no_config"
    elif any(issue.severity == "error" for issue in issues):
        overall = "blocked"
    else:
        overall = "ready"

    return {
        "schema_version": 1,
        "overall": overall,
        "config_files": configs,
        "servers": servers,
        "server_count": len(servers),
        "issues": [issue.as_dict() for issue in issues],
        "security": {
            "executes_tools": False,
            "reads_env_values": False,
            "prints_credentials": False,
            "credential_values_require_env_interpolation": True,
        },
    }


def mcp_policy_check(payload: Mapping[str, Any], *, discovery: Mapping[str, Any] | None = None) -> dict[str, Any]:
    operation = str(payload.get("operation") or "").strip()
    server = str(payload.get("server") or "").strip()
    tool = payload.get("tool")
    if operation not in {"status", "list-tools", "call-tool"}:
        return {"decision": "DENY", "reason": "unsupported MCP operation", "executed": False}
    if operation != "status" and not server:
        return {"decision": "DENY", "reason": "MCP server is required", "executed": False}
    if discovery and discovery.get("overall") == "blocked":
        return {"decision": "DENY", "reason": "MCP config is blocked", "executed": False}
    if operation == "call-tool":
        return {
            "decision": "DENY",
            "reason": "MCP tool execution is not enabled in this foundation milestone",
            "executed": False,
            "server": server,
            "tool": tool if isinstance(tool, str) else None,
        }
    return {
        "decision": "ALLOW",
        "reason": f"MCP {operation} is read-only and does not execute external tools",
        "executed": False,
        "server": server or None,
        "tool": tool if isinstance(tool, str) else None,
    }
