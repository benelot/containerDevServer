#!/usr/bin/env bash
# Verifies every ${VAR} reference in docker-compose.yml is documented in .env.example.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/helpers.sh"

echo "── .env coverage ────────────────────────────────"

for svc_dir in "${REPO_ROOT}"/services/*/; do
    svc=$(basename "$svc_dir")
    compose="${svc_dir}docker-compose.yml"
    env_file="${svc_dir}.env.example"
    [[ -f "$compose" && -f "$env_file" ]] || continue

    # Extract all variable names: both ${VAR} and ${VAR:-default}
    while IFS= read -r var; do
        [[ -z "$var" ]] && continue
        if grep -q "^${var}=" "$env_file"; then
            pass "${svc}: ${var}"
        else
            fail "${svc}: ${var} used in compose but absent from .env.example"
        fi
    done < <(grep -oE '\$\{[A-Z_0-9]+[^}]*\}' "$compose" \
              | sed 's/\${//; s/[:-].*//' \
              | sort -u)
done

summary ".env coverage"
