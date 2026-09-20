#!/usr/bin/env bash
# Run all test suites.  Pass --integration to also run smoke tests.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INTEGRATION=0
for arg in "$@"; do
    case "$arg" in
        --integration) INTEGRATION=1 ;;
        --help|-h)
            echo "Usage: $0 [--integration]"
            echo "  --integration  Also run smoke tests (starts real Docker stacks)"
            exit 0 ;;
    esac
done
export INTEGRATION

TOTAL_PASS=0; TOTAL_FAIL=0; TOTAL_SKIP=0

run_suite() {
    local output
    output=$(bash "$1" 2>&1)
    echo "$output"
    local p f s
    p=$(echo "$output" | grep -oP '\d+(?= passed)'  | tail -1 || true); p=${p:-0}
    f=$(echo "$output" | grep -oP '\d+(?= failed)'  | tail -1 || true); f=${f:-0}
    s=$(echo "$output" | grep -oP '\d+(?= skipped)' | tail -1 || true); s=${s:-0}
    ((TOTAL_PASS+=p, TOTAL_FAIL+=f, TOTAL_SKIP+=s)) || true
}

echo ""
echo "======================================================="
echo "  Container Dev Server -- Test Suite"
echo "======================================================="
echo ""

for suite in structure yaml env_coverage ansible compose_config smoke; do
    script="${SCRIPT_DIR}/test_${suite}.sh"
    [[ -f "$script" ]] && run_suite "$script" && echo ""
done

echo "======================================================="
printf "  TOTAL  %d passed  %d failed  %d skipped\n" \
    "$TOTAL_PASS" "$TOTAL_FAIL" "$TOTAL_SKIP"
echo "======================================================="
echo ""

[[ $TOTAL_FAIL -eq 0 ]]
