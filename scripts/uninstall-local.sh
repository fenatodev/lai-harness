#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: lai-uninstall [--delete-data]"
}

bin_dir="${LAI_BIN_DIR:-$HOME/.local/bin}"
data_dir="${LAI_DATA_DIR:-$HOME/.local/share/lai}"
config_dir="${LAI_CONFIG_DIR:-$HOME/.config/lai}"
delete_data=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --delete-data)
            delete_data=1
            shift
            ;;
        --help|-h|help)
            usage
            exit 0
            ;;
        *)
            usage >&2
            exit 2
            ;;
    esac
done

for name in \
    lai local-agent lai_semantics.py lai_config.py lai_specs.py lai_sessions.py \
    lai_mcp.py lai_web.py lai-doctor lai-server-start start-secure.ps1 lai-server-stop \
    lai-server-restart lai-uninstall; do
    rm -f -- "$bin_dir/$name"
done

echo "Removed lai harness binaries from $bin_dir."

if [ "$delete_data" -eq 1 ]; then
    rm -rf -- "$data_dir" "$config_dir"
    echo "Deleted lai harness data/config directories by explicit --delete-data request."
else
    echo "Preserved lai harness data at $data_dir."
    echo "Preserved lai harness config at $config_dir."
    echo "Preserved lai harness distribution state under $data_dir/distribution."
fi
