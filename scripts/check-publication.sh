#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

failed=0
check_forbidden() {
    local label="$1"
    local pattern="$2"
    if rg -n -i --hidden \
        --glob '!.git/**' \
        --glob '!scripts/check-publication.sh' \
        --glob '!scripts/package-vsix.sh' \
        "$pattern" .; then
        echo "publication check failed: $label" >&2
        failed=1
    fi
}

check_forbidden "private project name" 'business-automation'
check_forbidden "personal Linux path" '/home/fenato/'
check_forbidden "personal Windows path" 'C:\\Users\\fenat'
check_forbidden "private-key material" 'BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY'
check_forbidden "common committed secret assignment" '(api[_-]?key|password|token|secret)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9+/=_-]{24,}'

if find . -type f \( -name '*.gguf' -o -name '*.vsix' -o -name 'events.jsonl' -o -name 'current-context.*' -o -name 'api-key*' -o -name '*.key' -o -name '*.log' \) -print | grep -q .; then
    echo "publication check failed: private/generated artifact present" >&2
    find . -type f \( -name '*.gguf' -o -name '*.vsix' -o -name 'events.jsonl' -o -name 'current-context.*' -o -name 'api-key*' -o -name '*.key' -o -name '*.log' \) -print >&2
    failed=1
fi

if [[ "$failed" -ne 0 ]]; then
    exit 1
fi

echo "Publication scan passed: no forbidden private paths, project names, key material, or runtime artifacts found."
