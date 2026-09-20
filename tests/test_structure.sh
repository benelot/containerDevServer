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

for svc in mlflow dvc label-studio jupyterlab dagster evidently bentoml monitoring; do
    check_file "services/${svc}/docker-compose.yml"
    check_file "services/${svc}/.env.example"
done

check_file "services/dagster/Dockerfile"
check_file "services/dagster/dagster.yaml"
check_file "services/dagster/workspace.yaml"
check_file "services/dagster/requirements.txt"
check_file "services/dagster/pipelines/mnist1d_pipeline.py"
check_file "services/evidently/Dockerfile"
check_file "services/bentoml/Dockerfile"
check_file "services/bentoml/service.py"
check_file "services/labs/Dockerfile"
check_file "services/labs/docker-compose.yml"
check_file "services/labs/.env.example"
check_file "services/labs/main.py"
check_file "services/labs/entrypoint.sh"
check_file "services/labs/hugo.toml"
check_file "services/labs/requirements.txt"
check_file "services/labs/scripts/generate_ports_data.py"
check_file "services/labs/content/_index.md"
check_file "scripts/generate-ports.sh"

check_file  "scripts/start.sh"
check_exec  "scripts/start.sh"
check_file  "scripts/backup.sh"
check_exec  "scripts/backup.sh"
check_file  "scripts/generate_notebooks.py"
check_file  "scripts/generate_data_quality_notebook.py"
check_file  "notebooks/mnist1d_crisp_dm.ipynb"
check_file  "notebooks/data_quality.ipynb"
check_file  "README.md"
check_file  "CLAUDE.md"

summary "Structure"
