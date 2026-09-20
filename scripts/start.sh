#!/usr/bin/env bash
# Usage: ./scripts/start.sh [service] [--random] [--stop] [--help]
#   service   mlflow (default)
#   --random  assign fresh random ports and save them to .env
#   --stop    stop the stack instead of starting it
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SERVICE="mlflow"
RANDOM_PORTS=false
STOP=false

# ── Argument parsing ──────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --random) RANDOM_PORTS=true ;;
    --stop)   STOP=true ;;
    --help|-h)
      echo "Usage: $0 [service] [--random] [--stop]"
      echo "  service   Service directory under services/ (default: mlflow)"
      echo "  --random  Assign unused random ports; written back to .env"
      echo "  --stop    Stop the running stack"
      exit 0
      ;;
    --*) echo "Unknown flag: $arg  (try --help)"; exit 1 ;;
    *)   SERVICE="$arg" ;;
  esac
done

SERVICE_DIR="${REPO_ROOT}/services/${SERVICE}"
ENV_FILE="${SERVICE_DIR}/.env"

if [[ ! -d "${SERVICE_DIR}" ]]; then
  echo "Error: no service directory at ${SERVICE_DIR}"
  exit 1
fi

# ── Stop path ─────────────────────────────────────────────────────────────────
if [[ "${STOP}" == "true" ]]; then
  echo "Stopping ${SERVICE} stack..."
  docker compose -f "${SERVICE_DIR}/docker-compose.yml" \
    ${ENV_FILE:+--env-file "${ENV_FILE}"} down
  exit 0
fi

# ── Bootstrap .env from example if missing ───────────────────────────────────
if [[ ! -f "${ENV_FILE}" ]]; then
  if [[ -f "${SERVICE_DIR}/.env.example" ]]; then
    cp "${SERVICE_DIR}/.env.example" "${ENV_FILE}"
    echo "Created ${ENV_FILE} from .env.example"
  else
    touch "${ENV_FILE}"
  fi
fi

# ── Random port assignment ────────────────────────────────────────────────────
find_free_port() {
  local port
  while true; do
    port=$(shuf -i 10000-60000 -n 1)
    if ! ss -tln 2>/dev/null | grep -qE ":${port}[[:space:]]|:${port}$"; then
      echo "$port"
      return
    fi
  done
}

set_env_var() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "${ENV_FILE}"; then
    sed -i "s|^${key}=.*|${key}=${val}|" "${ENV_FILE}"
  else
    echo "${key}=${val}" >> "${ENV_FILE}"
  fi
}

if [[ "${RANDOM_PORTS}" == "true" ]]; then
  echo "Assigning random ports..."
  # Collect all PORT= vars from the env file and randomise each one
  port_vars=$(grep -oE '^[A-Z_]*PORT[A-Z_]*=' "${ENV_FILE}" | tr -d '=')
  for var in $port_vars; do
    port=$(find_free_port)
    set_env_var "$var" "$port"
    echo "  ${var}=${port}"
  done
fi

# ── Load .env for display ─────────────────────────────────────────────────────
set -a
# shellcheck source=/dev/null
source "${ENV_FILE}"
set +a

# ── Start the stack ───────────────────────────────────────────────────────────
echo ""
echo "Starting ${SERVICE} stack..."
docker compose -f "${SERVICE_DIR}/docker-compose.yml" --env-file "${ENV_FILE}" up -d --build

HOST="${HOSTNAME:-localhost}"

# ── Print service URLs ────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "  ${SERVICE^^} STACK  --  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

case "${SERVICE}" in
  mlflow)
    echo ""
    echo "  MLflow Tracking UI    http://${HOST}:${MLFLOW_PORT:-5000}"
    echo "  MinIO Console         http://${HOST}:${MINIO_CONSOLE_PORT:-9001}"
    echo "  MinIO S3 API          http://${HOST}:${MINIO_API_PORT:-9000}"
    echo "  PostgreSQL            ${HOST}:${POSTGRES_PORT:-5432}  db=${POSTGRES_DB:-mlflow}"
    echo ""
    echo "  Python client:"
    echo "    import mlflow"
    echo "    mlflow.set_tracking_uri('http://${HOST}:${MLFLOW_PORT:-5000}')"
    echo ""
    echo "  Credentials: ${ENV_FILE}"
    ;;
  dvc)
    echo ""
    echo "  MinIO Console         http://${HOST}:${MINIO_CONSOLE_PORT:-9011}"
    echo "  MinIO S3 API          http://${HOST}:${MINIO_API_PORT:-9010}"
    echo ""
    echo "  DVC remote config (run once in your repo):"
    echo "    dvc remote add -d myremote s3://${MINIO_BUCKET:-dvc-cache}"
    echo "    dvc remote modify myremote endpointurl http://${HOST}:${MINIO_API_PORT:-9010}"
    echo "    dvc remote modify myremote access_key_id ${MINIO_ROOT_USER:-minioadmin}"
    echo "    dvc remote modify myremote secret_access_key ${MINIO_ROOT_PASSWORD:-minioadmin_secret}"
    echo ""
    echo "  Credentials: ${ENV_FILE}"
    ;;
  label-studio)
    echo ""
    echo "  Label Studio UI       http://${HOST}:${LABEL_STUDIO_PORT:-8080}"
    echo "  Login                 ${LABEL_STUDIO_USERNAME:-admin@example.com}"
    echo "  PostgreSQL            ${HOST}:${POSTGRES_PORT:-5433}  db=${POSTGRES_DB:-labelstudio}"
    echo ""
    echo "  Credentials: ${ENV_FILE}"
    ;;
  jupyterlab)
    echo ""
    echo "  JupyterLab            http://${HOST}:${JUPYTER_PORT:-8888}/?token=${JUPYTER_TOKEN:-changeme}"
    echo ""
    echo "  Credentials: ${ENV_FILE}"
    ;;
  dagster)
    echo ""
    echo "  Dagster UI            http://${HOST}:${DAGSTER_PORT:-3000}"
    echo "  PostgreSQL            ${HOST}:${POSTGRES_PORT:-5434}  db=${POSTGRES_DB:-dagster}"
    echo ""
    echo "  Launch the pipeline from the UI or:"
    echo "    docker compose -f services/dagster/docker-compose.yml exec dagster-webserver \\"
    echo "      dagster job execute -j mnist1d_full_pipeline -m pipelines.mnist1d_pipeline"
    echo ""
    echo "  Credentials: ${ENV_FILE}"
    ;;
  evidently)
    echo ""
    echo "  Evidently UI          http://${HOST}:${EVIDENTLY_PORT:-8001}"
    echo ""
    echo "  Push a snapshot from Python:"
    echo "    from evidently.ui.workspace import Workspace"
    echo "    ws = Workspace('http://${HOST}:${EVIDENTLY_PORT:-8001}')"
    echo ""
    echo "  Credentials: ${ENV_FILE}"
    ;;
  *)
    echo "  Stack started. Check 'docker compose ps' for port details."
    ;;
esac

echo "============================================================"
echo ""
