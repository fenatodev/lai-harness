#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
extension_dir="$repo_root/vscode-extension"
version="$(node -p "require('$extension_dir/package.json').version")"
output="${1:-/tmp/lai-local-agent-${version}.vsix}"

(cd "$extension_dir" && npx --yes @vscode/vsce@3.9.2 package --out "$output")

expected="$(printf '%s\n' \
    '[Content_Types].xml' \
    'extension.vsixmanifest' \
    'extension/LICENSE.txt' \
    'extension/extension.js' \
    'extension/package.json' \
    'extension/readme.md' | sort)"
actual="$(unzip -Z1 "$output" | sort)"

if [[ "$actual" != "$expected" ]]; then
    echo "Unexpected VSIX content:" >&2
    unzip -l "$output" >&2
    exit 1
fi

scan_file="$(mktemp)"
trap 'rm -f "$scan_file"' EXIT

if ! unzip -p "$output" \
    extension.vsixmanifest \
    extension/LICENSE.txt \
    extension/extension.js \
    extension/package.json \
    extension/readme.md \
    > "$scan_file"; then
    echo "VSIX private-content scan could not read packaged files." >&2
    exit 1
fi

set +e
scan_matches="$(
    grep -Ein \
        '(business-automation|/home/fenato/|C:\\Users\\fenat|BEGIN .*PRIVATE KEY)' \
        "$scan_file"
)"
scan_rc=$?
set -e

if [[ "$scan_rc" -eq 0 ]]; then
    printf '%s\n' "$scan_matches" >&2
    echo "Private content found in VSIX." >&2
    exit 1
fi

if [[ "$scan_rc" -ne 1 ]]; then
    echo "VSIX private-content scan failed with code $scan_rc." >&2
    exit 1
fi

echo "VSIX inspection passed: $output"
