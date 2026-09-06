from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Mapping, NoReturn, Sequence, TypeAlias


DEFAULT_MODEL = "mistralai/Ministral-3-8B-Instruct-2512-GGUF:Q4_K_M"

ConfigValue: TypeAlias = str | int | Path | None
Config: TypeAlias = dict[str, ConfigValue]

CONFIG_OPTIONS: dict[str, str] = {
    "--config": "config_file",
    "--config-dir": "config_dir",
    "--host": "host",
    "--port": "port",
    "--model": "model",
    "--api-key-file": "api_key_file",
    "--control-api-key-file": "control_api_key_file",
    "--data-dir": "data_dir",
    "--skills-dir": "skills_dir",
    "--state-dir": "state_dir",
    "--metrics-dir": "metrics_dir",
    "--audit-dir": "audit_dir",
    "--state-retention-days": "state_retention_days",
    "--metrics-max-bytes": "metrics_max_bytes",
    "--metrics-keep-lines": "metrics_keep_lines",
    "--audit-max-bytes": "audit_max_bytes",
    "--audit-keep-lines": "audit_keep_lines",
    "--llama-server": "llama_server",
    "--server-launcher": "server_launcher",
    "--chat-template": "chat_template",
}

CONFIG_VALUE_KEYS: set[str] = {
    "host",
    "port",
    "model",
    "config_dir",
    "config_file",
    "data_dir",
    "api_key_file",
    "control_api_key_file",
    "skills_dir",
    "state_dir",
    "metrics_dir",
    "audit_dir",
    "state_retention_days",
    "metrics_max_bytes",
    "metrics_keep_lines",
    "audit_max_bytes",
    "audit_keep_lines",
    "llama_server",
    "server_launcher",
    "chat_template",
}
CONFIG_FILE_KEYS: set[str] = CONFIG_VALUE_KEYS - {"config_dir", "config_file"}
CONFIG_PATH_KEYS: set[str] = {
    "config_dir",
    "config_file",
    "data_dir",
    "api_key_file",
    "control_api_key_file",
    "skills_dir",
    "state_dir",
    "metrics_dir",
    "audit_dir",
    "llama_server",
    "chat_template",
}
CONFIG_OPTIONAL_STRING_KEYS: set[str] = {"host"}
CONFIG_REQUIRED_STRING_KEYS: set[str] = {"model", "server_launcher"}
CONFIG_INTEGER_LIMITS: dict[str, tuple[int, int]] = {
    "state_retention_days": (1, 3650),
    "metrics_max_bytes": (1, 1_000_000_000),
    "metrics_keep_lines": (1, 1_000_000),
    "audit_max_bytes": (1, 1_000_000_000),
    "audit_keep_lines": (1, 1_000_000),
}
CONFIG_DIRECTORY_KEYS: set[str] = {
    "config_dir",
    "data_dir",
    "skills_dir",
    "state_dir",
    "metrics_dir",
    "audit_dir",
}


def config_error(message: str, config_file: object = None) -> NoReturn:
    if config_file:
        raise SystemExit(f"Invalid lai config {config_file}: {message}")
    raise SystemExit(f"Invalid lai configuration: {message}")


def validate_config_mapping(
    mapping: Mapping[str, object],
    *,
    config_file: object = None,
    file_scope: bool = False,
) -> None:
    allowed = CONFIG_FILE_KEYS if file_scope else CONFIG_VALUE_KEYS
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        config_error(f"unknown key(s): {', '.join(unknown)}", config_file)


def require_config_string(
    key: str,
    value: object,
    *,
    config_file: object = None,
    optional: bool = False,
) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str):
        config_error(f"{key} must be a string", config_file)
    if not value.strip():
        config_error(f"{key} must not be empty", config_file)
    if "\x00" in value:
        config_error(f"{key} must not contain NUL bytes", config_file)
    return value


def normalize_config_path(
    key: str,
    value: object,
    *,
    config_file: object = None,
) -> Path | None:
    if value is None:
        return None
    if not isinstance(value, (str, os.PathLike)):
        config_error(f"{key} must be a filesystem path string", config_file)
    text = str(value)
    if not text.strip():
        config_error(f"{key} must not be empty", config_file)
    if "\x00" in text:
        config_error(f"{key} must not contain NUL bytes", config_file)
    return Path(text).expanduser()


def _bounded_integer(
    key: str,
    value: object,
    minimum: int,
    maximum: int,
    *,
    config_file: object = None,
) -> int:
    if isinstance(value, bool):
        config_error(f"{key} must be an integer from {minimum} to {maximum}", config_file)
    if isinstance(value, (int, float, str)):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            config_error(
                f"{key} must be an integer from {minimum} to {maximum}",
                config_file,
            )
    else:
        config_error(f"{key} must be an integer from {minimum} to {maximum}", config_file)
    if not minimum <= parsed <= maximum:
        config_error(f"{key} must be an integer from {minimum} to {maximum}", config_file)
    return parsed


def normalize_config_values(
    values: Mapping[str, object],
    *,
    config_file: object = None,
    file_scope: bool = False,
) -> Config:
    validate_config_mapping(values, config_file=config_file, file_scope=file_scope)
    normalized: dict[str, object] = dict(values)

    if "port" in normalized:
        normalized["port"] = _bounded_integer(
            "port", normalized["port"], 1, 65535, config_file=config_file
        )

    for key, (minimum, maximum) in CONFIG_INTEGER_LIMITS.items():
        if key in normalized:
            normalized[key] = _bounded_integer(
                key,
                normalized[key],
                minimum,
                maximum,
                config_file=config_file,
            )

    for key in CONFIG_REQUIRED_STRING_KEYS:
        if key in normalized:
            normalized[key] = require_config_string(
                key, normalized[key], config_file=config_file
            )

    for key in CONFIG_OPTIONAL_STRING_KEYS:
        if key not in normalized:
            continue
        normalized[key] = require_config_string(
            key, normalized[key], config_file=config_file, optional=True
        )
        host = normalized[key]
        if isinstance(host, str) and (
            any(ch.isspace() for ch in host) or "://" in host or "/" in host
        ):
            config_error(
                "host must be a hostname or IP address, not a URL or path",
                config_file,
            )

    for key in CONFIG_PATH_KEYS:
        if key in normalized:
            normalized[key] = normalize_config_path(
                key, normalized[key], config_file=config_file
            )

    result: Config = {}
    for key, value in normalized.items():
        if value is None or isinstance(value, (str, int, Path)):
            result[key] = value
        else:
            config_error(f"{key} has an unsupported value type", config_file)
    return result


def load_configuration(
    argv: Sequence[str],
    environ: Mapping[str, str] | None = None,
    home: str | os.PathLike[str] | None = None,
) -> tuple[Config, list[str]]:
    effective_env = dict(os.environ if environ is None else environ)
    home_path = Path.home() if home is None else Path(home)
    remaining = list(argv)
    cli_raw: dict[str, object] = {}

    while remaining and remaining[0] in CONFIG_OPTIONS:
        option = remaining.pop(0)
        if not remaining:
            raise SystemExit(f"Missing value for {option}")
        cli_raw[CONFIG_OPTIONS[option]] = remaining.pop(0)

    cli = normalize_config_values(cli_raw)
    default_config_dir = Path(
        effective_env.get(
            "LAI_CONFIG_DIR",
            str(Path(effective_env.get("XDG_CONFIG_HOME", home_path / ".config")) / "lai"),
        )
    ).expanduser()
    cli_config_dir = cli.get("config_dir")
    if cli_config_dir is not None and not isinstance(cli_config_dir, Path):
        config_error("config_dir did not normalize to a path")
    config_dir = (cli_config_dir or default_config_dir).expanduser()

    cli_config_file = cli.get("config_file")
    if cli_config_file is not None and not isinstance(cli_config_file, Path):
        config_error("config_file did not normalize to a path")
    config_file = (
        cli_config_file
        or Path(effective_env.get("LAI_CONFIG_FILE", str(config_dir / "config.toml")))
    ).expanduser()

    file_values: Config = {}
    if config_file.is_file():
        try:
            document = tomllib.loads(config_file.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            config_error(str(exc), config_file)
        file_section = document.get("lai", {})
        if not isinstance(file_section, dict):
            config_error("[lai] must be a TOML table", config_file)
        file_values = normalize_config_values(
            file_section, config_file=config_file, file_scope=True
        )

    default_data_dir = Path(
        effective_env.get("XDG_DATA_HOME", str(home_path / ".local" / "share"))
    ) / "lai"
    defaults: Config = {
        "host": None,
        "port": 8080,
        "model": DEFAULT_MODEL,
        "config_dir": config_dir,
        "config_file": config_file,
        "data_dir": default_data_dir,
        "api_key_file": config_dir / "llama-api-key",
        "control_api_key_file": config_dir / "control-api-key",
        "skills_dir": None,
        "state_dir": None,
        "metrics_dir": None,
        "audit_dir": None,
        "state_retention_days": 45,
        "metrics_max_bytes": 5_000_000,
        "metrics_keep_lines": 3000,
        "audit_max_bytes": 5_000_000,
        "audit_keep_lines": 4000,
        "llama_server": None,
        "server_launcher": "lai-server-start",
        "chat_template": None,
    }
    env_names = {key: "LAI_" + key.upper() for key in defaults}
    env_values: dict[str, object] = {
        key: effective_env[name]
        for key, name in env_names.items()
        if name in effective_env
    }
    values: Config = {**defaults, **file_values}
    values.update(normalize_config_values(env_values))
    values.update(cli)
    values = normalize_config_values(values)

    data_dir = values["data_dir"]
    if not isinstance(data_dir, Path):
        config_error("data_dir did not normalize to a path", config_file)
    fallbacks: dict[str, Path] = {
        "config_dir": config_dir,
        "config_file": config_file,
        "data_dir": data_dir,
        "api_key_file": config_dir / "llama-api-key",
        "control_api_key_file": config_dir / "control-api-key",
        "skills_dir": data_dir / "skills",
        "state_dir": data_dir / "state",
        "metrics_dir": data_dir / "metrics",
        "audit_dir": data_dir / "audit",
    }
    for key, fallback in fallbacks.items():
        values[key] = normalize_config_path(key, values.get(key) or fallback)

    return values, remaining


def path_status(
    path: Path,
    *,
    expect_dir: bool = False,
    expect_file: bool = False,
    secret: bool = False,
) -> str:
    try:
        if path.exists():
            if expect_dir and not path.is_dir():
                return "ERROR: exists but is not a directory"
            if expect_file and not path.is_file():
                return "ERROR: exists but is not a file"
            if secret and path.is_file() and path.stat().st_size <= 0:
                return "ERROR: file is empty"
            return "OK"
        parent = path.parent
        if parent.exists() and not parent.is_dir():
            return "ERROR: parent exists but is not a directory"
        return "MISSING"
    except OSError as exc:
        return f"ERROR: {exc}"


def _required_path(config: Mapping[str, ConfigValue], key: str) -> Path:
    value = config[key]
    if not isinstance(value, Path):
        raise TypeError(f"{key} must be a normalized Path")
    return value


def render_config_status(config: Mapping[str, ConfigValue], version: str) -> str:
    lines = ["# lai config", f"Version: {version}", "", "Effective values:"]
    for key in sorted(config):
        value = config[key]
        shown = str(value) if isinstance(value, Path) else value
        lines.append(f"- {key}: {shown if shown is not None else '[auto]'}")

    checks: list[tuple[str, Path, bool, bool, bool]] = [
        ("config_file", _required_path(config, "config_file"), False, True, False),
        ("config_dir", _required_path(config, "config_dir"), True, False, False),
        ("api_key_file", _required_path(config, "api_key_file"), False, True, True),
        (
            "control_api_key_file",
            _required_path(config, "control_api_key_file"),
            False,
            True,
            True,
        ),
        ("data_dir", _required_path(config, "data_dir"), True, False, False),
        ("skills_dir", _required_path(config, "skills_dir"), True, False, False),
        ("state_dir", _required_path(config, "state_dir"), True, False, False),
        ("metrics_dir", _required_path(config, "metrics_dir"), True, False, False),
        ("audit_dir", _required_path(config, "audit_dir"), True, False, False),
    ]
    if config.get("llama_server"):
        checks.append(
            ("llama_server", _required_path(config, "llama_server"), False, True, False)
        )
    if config.get("chat_template"):
        checks.append(
            ("chat_template", _required_path(config, "chat_template"), False, True, False)
        )

    lines.extend(["", "Checks:"])
    for key, path, expect_dir, expect_file, secret in checks:
        status = path_status(
            path,
            expect_dir=expect_dir,
            expect_file=expect_file,
            secret=secret,
        )
        lines.append(f"- {key}: {status}")
    lines.extend(
        [
            "",
            "Notes:",
            "- MISSING means the path does not exist yet; it is not fatal for deterministic commands.",
            "- API key and control token contents are never printed.",
        ]
    )
    return "\n".join(lines)
