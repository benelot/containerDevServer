#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/helpers.sh"

echo "── Structure ────────────────────────────────────"

check_file() {
    [[ -f "${REPO_ROOT}/$1" ]] && pass "$1" || fail "$1 missing"
}
check_exec() {
    [[ -x "${REPO_ROOT}/$1" ]] && pass "$1 executable" || fail "$1 not executable"
}

check_file "ansible/playbook.yml"
check_file "ansible/inventory/hosts.yml"
check_file "ansible/roles/docker/tasks/main.yml"
check_file "ansible/roles/docker/defaults/main.yml"
check_file "ansible/roles/docker_config/tasks/main.yml"
check_file "ansible/roles/docker_config/handlers/main.yml"
check_file "ansible/roles/docker_config/defaults/main.yml"

for svc in mlflow dvc label-studio jupyterlab; do
    check_file "services/${svc}/docker-compose.yml"
    check_file "services/${svc}/.env.example"
done

check_file  "scripts/start.sh"
check_exec  "scripts/start.sh"
check_file  "README.md"
check_file  "CLAUDE.md"

summary "Structure"
