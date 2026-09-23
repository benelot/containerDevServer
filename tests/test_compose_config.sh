#!/usr/bin/env bash
# Validates each compose file with 'docker compose config'.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/helpers.sh"

echo "── Docker Compose config ────────────────────────"

if ! has_cmd docker; then
    skip "All compose config tests" "docker not installed"
    summary "Compose config"; exit 0
fi

for svc_dir in "${REPO_ROOT}"/services/*/; do
    svc=$(basename "$svc_dir")
    compose="${svc_dir}docker-compose.yml"
    env_file="${svc_dir}.env.example"
    [[ -f "$compose" ]] || continue

    env_arg=()
    [[ -f "$env_file" ]] && env_arg=(--env-file "$env_file")

    if docker compose -f "$compose" "${env_arg[@]}" config --quiet 2>/dev/null; then
        pass "${svc}: compose config"
    else
        fail "${svc}: compose config invalid"
        docker compose -f "$compose" "${env_arg[@]}" config 2>&1 | sed 's/^/    /'
    fi
done

summary "Compose config"
