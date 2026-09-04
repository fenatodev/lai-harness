#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

failed=0
scan_forbidden() {
    local pattern="$1"

    if command -v rg >/dev/null 2>&1; then
        rg -n -i --hidden \
            --glob '!.git/**' \
            --glob '!.venv/**' \
            --glob '!scripts/check-publication.sh' \
            --glob '!scripts/package-vsix.sh' \
            "$pattern" .
        return $?
    fi

    if command -v grep >/dev/null 2>&1; then
        grep -RInEi \
            --exclude-dir=.git \
            --exclude-dir=.venv \
            --exclude='check-publication.sh' \
            --exclude='package-vsix.sh' \
            "$pattern" .
        return $?
    fi

    echo "publication scanner unavailable: neither rg nor grep found" >&2
    return 127
}

check_forbidden() {
    local label="$1"
    local pattern="$2"
    local output
    local status

    if output="$(scan_forbidden "$pattern")"; then
        status=0
    else
        status=$?
    fi

    case "$status" in
        0)
            printf '%s\n' "$output"
            echo "publication check failed: $label" >&2
            failed=1
            ;;
        1)
            ;;
        *)
            echo "publication check failed: scanner error for $label (exit $status)" >&2
            failed=1
            ;;
    esac
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
