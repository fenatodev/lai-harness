#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
bin_dir="${LAI_BIN_DIR:-$HOME/.local/bin}"
data_dir="${LAI_DATA_DIR:-$HOME/.local/share/lai}"

install -d "$bin_dir" "$data_dir/skills" "$data_dir/model-eval" "$data_dir/update-intelligence" "$data_dir/distribution"

dist_dir="$data_dir/distribution"
state_file="$dist_dir/installed-state.json"
rollback_dir="$dist_dir/rollback/previous"
previous_version=""
if [ -f "$state_file" ]; then
    previous_version="$(python3 - "$state_file" <<'STATEPY'
import json, sys
try:
    data = json.loads(open(sys.argv[1], encoding="utf-8").read())
    value = data.get("version")
    print(value if isinstance(value, str) else "")
except Exception:
    print("")
STATEPY
)"
fi
rm -rf -- "$rollback_dir"
install -d "$rollback_dir"
backup_count=0
for name in \
    lai local-agent lai_semantics.py lai_config.py lai_specs.py lai_sessions.py \
    lai_mcp.py lai_web.py lai-doctor lai-server-start lai-server-stop \
    lai-server-restart lai-uninstall; do
    if [ -f "$bin_dir/$name" ]; then
        cp -p -- "$bin_dir/$name" "$rollback_dir/$name"
        backup_count=$((backup_count + 1))
    fi
done
install -m 0755 "$repo_root/src/local-agent" "$bin_dir/local-agent"
install -m 0644 "$repo_root/src/lai_semantics.py" "$bin_dir/lai_semantics.py"
install -m 0644 "$repo_root/src/lai_config.py" "$bin_dir/lai_config.py"
install -m 0644 "$repo_root/src/lai_specs.py" "$bin_dir/lai_specs.py"
install -m 0644 "$repo_root/src/lai_sessions.py" "$bin_dir/lai_sessions.py"
install -m 0644 "$repo_root/src/lai_mcp.py" "$bin_dir/lai_mcp.py"
install -m 0644 "$repo_root/src/lai_web.py" "$bin_dir/lai_web.py"
install -m 0755 "$repo_root/src/lai" "$bin_dir/lai"
install -m 0755 "$repo_root/scripts/ministral-doctor" "$bin_dir/lai-doctor"
install -m 0755 "$repo_root/scripts/ministral-start" "$bin_dir/lai-server-start"
install -m 0755 "$repo_root/scripts/ministral-stop" "$bin_dir/lai-server-stop"
install -m 0755 "$repo_root/scripts/ministral-restart" "$bin_dir/lai-server-restart"
install -m 0755 "$repo_root/scripts/uninstall-local.sh" "$bin_dir/lai-uninstall"
install -m 0644 "$repo_root"/skills/*.txt "$data_dir/skills/"
install -m 0644 "$repo_root/model-eval/fixtures-v1.json" "$data_dir/model-eval/fixtures-v1.json"
install -m 0644 "$repo_root/updates/sources-v1.json" "$data_dir/update-intelligence/sources-v1.json"

for skill_dir in "$repo_root"/.agents/skills/*; do
    [ -d "$skill_dir" ] || continue
    name="$(basename "$skill_dir")"
    install -d "$data_dir/skills/$name"
    install -m 0644 "$skill_dir/SKILL.md" "$data_dir/skills/$name/SKILL.md"
done


version="$("$repo_root/src/local-agent" --version | awk '{print $NF}')"
python3 - "$state_file" "$version" "$previous_version" "$backup_count" <<'STATEPY'
import json
import os
import sys
from pathlib import Path

state_file = Path(sys.argv[1])
version = sys.argv[2]
previous_version = sys.argv[3] or None
backup_count = int(sys.argv[4])
components = [
    "lai",
    "local-agent",
    "lai_semantics.py",
    "lai_config.py",
    "lai_specs.py",
    "lai_sessions.py",
    "lai_mcp.py",
    "lai_web.py",
    "lai-doctor",
    "lai-server-start",
    "lai-server-stop",
    "lai-server-restart",
    "lai-uninstall",
]
payload = {
    "schema_version": 1,
    "product": "lai harness",
    "version": version,
    "previous_version": previous_version,
    "components": components,
    "core_stdlib_only": True,
    "optional_components_explicit": True,
    "model_runtime_count_policy": "one",
    "rollback": {
        "backup_available": backup_count > 0,
        "file_count": backup_count,
        "automatic": False,
    },
    "publication": {
        "release_created": False,
        "tag_created": False,
        "push_performed": False,
        "vsix_published": False,
    },
    "uninstall": {
        "preserve_data_by_default": True,
        "delete_data_requires_explicit_flag": True,
    },
}
state_file.parent.mkdir(parents=True, exist_ok=True)
tmp = state_file.with_name(f".{state_file.name}.{os.getpid()}.tmp")
tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
os.replace(tmp, state_file)
os.chmod(state_file, 0o600)
STATEPY

echo "Installed lai harness as lai/local-agent in $bin_dir and skills in $data_dir/skills."
echo "The VS Code extension is installed separately; see docs/INSTALLATION.md."
