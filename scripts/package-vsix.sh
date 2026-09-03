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

if unzip -p "$output" \
    extension.vsixmanifest \
    extension/LICENSE.txt \
    extension/extension.js \
    extension/package.json \
    extension/readme.md \
    | rg -n -i '(business-automation|/home/fenato/|C:\\Users\\fenat|BEGIN .*PRIVATE KEY)'; then
    echo "Private content found in VSIX." >&2
    exit 1
fi

echo "VSIX inspection passed: $output"
