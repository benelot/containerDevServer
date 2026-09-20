#!/usr/bin/env bash
# Shared test helpers. Source this file; do not execute directly.
PASS=0; FAIL=0; SKIP=0
declare -a FAILURES=()

pass() { printf "  \033[32m✓\033[0m  %s\n" "$1"; ((PASS++)) || true; }
fail() { printf "  \033[31m✗\033[0m  %s\n" "$1"; ((FAIL++)) || true; FAILURES+=("$1"); }
skip() { printf "  \033[33m-\033[0m  %s  [skip: %s]\n" "$1" "$2"; ((SKIP++)) || true; }

has_cmd() { command -v "$1" &>/dev/null; }

summary() {
    local suite="${1:-Suite}"
    echo ""
    printf "  %-30s  %d passed  %d failed  %d skipped\n" \
        "$suite" "$PASS" "$FAIL" "$SKIP"
    if [[ ${#FAILURES[@]} -gt 0 ]]; then
        for f in "${FAILURES[@]}"; do printf "    \033[31m✗\033[0m %s\n" "$f"; done
    fi
    [[ $FAIL -eq 0 ]]
}
