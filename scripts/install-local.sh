#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
bin_dir="${LAI_BIN_DIR:-$HOME/.local/bin}"
data_dir="${LAI_DATA_DIR:-$HOME/.local/share/lai}"

install -d "$bin_dir" "$data_dir/skills"
install -m 0755 "$repo_root/src/local-agent" "$bin_dir/local-agent"
install -m 0755 "$repo_root/src/lai" "$bin_dir/lai"
install -m 0755 "$repo_root/scripts/ministral-doctor" "$bin_dir/lai-doctor"
install -m 0755 "$repo_root/scripts/ministral-start" "$bin_dir/lai-server-start"
install -m 0755 "$repo_root/scripts/ministral-stop" "$bin_dir/lai-server-stop"
install -m 0755 "$repo_root/scripts/ministral-restart" "$bin_dir/lai-server-restart"
install -m 0644 "$repo_root"/skills/*.txt "$data_dir/skills/"

echo "Installed lai/local-agent in $bin_dir and skills in $data_dir/skills."
echo "The VS Code extension is installed separately; see docs/INSTALLATION.md."
