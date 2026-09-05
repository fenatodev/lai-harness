#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests .cursor/hooks
python3 -m py_compile src/local-agent .cursor/hooks/*.py
make typecheck
node --check vscode-extension/extension.js
bash -n scripts/*.sh
python3 -m json.tool vscode-extension/package.json >/dev/null
git diff --check
./scripts/check-publication.sh
./scripts/package-vsix.sh "${1:-/tmp/lai-harness-validation.vsix}"

echo "All lai harness publication gates passed."
