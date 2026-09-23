#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/helpers.sh"

echo "── YAML syntax ──────────────────────────────────"

if ! has_cmd python3; then
    skip "All YAML tests" "python3 not installed"
    summary "YAML syntax"; exit 0
fi

check_yaml() {
    local f="${REPO_ROOT}/$1"
    if python3 -c "import yaml, sys; yaml.safe_load(open(sys.argv[1]))" "$f" 2>/dev/null; then
        pass "$1"
    else
        fail "$1 invalid YAML"
        python3 -c "import yaml, sys; yaml.safe_load(open(sys.argv[1]))" "$f" 2>&1 | sed 's/^/    /'
    fi
}

check_yaml "ansible/playbook.yml"
check_yaml "ansible/inventory/hosts.yml"
for role in docker docker_config; do
    check_yaml "ansible/roles/${role}/tasks/main.yml"
    check_yaml "ansible/roles/${role}/defaults/main.yml"
done
check_yaml "ansible/roles/docker_config/handlers/main.yml"

for svc in mlflow dvc label-studio jupyterlab; do
    check_yaml "services/${svc}/docker-compose.yml"
done

summary "YAML syntax"
