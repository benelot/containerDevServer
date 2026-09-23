#!/usr/bin/env bash
# Integration smoke test: starts MLflow stack, checks live endpoints, tears down.
# Requires INTEGRATION=1 to run (skipped by default -- takes several minutes).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/helpers.sh"

echo "── Smoke (integration) ──────────────────────────"

if [[ "${INTEGRATION:-0}" != "1" ]]; then
    skip "All smoke tests" "set INTEGRATION=1 to run"
    summary "Smoke"; exit 0
fi

if ! has_cmd docker; then
    skip "All smoke tests" "docker not installed"
    summary "Smoke"; exit 0
fi

if ! has_cmd curl; then
    skip "HTTP endpoint checks" "curl not installed"
fi

COMPOSE="${REPO_ROOT}/services/mlflow/docker-compose.yml"
ENV_FILE="${REPO_ROOT}/services/mlflow/.env.example"
PROJECT="mlflow-smoke-$$"

cleanup() {
    echo "  Tearing down test stack..."
    docker compose -f "$COMPOSE" --env-file "$ENV_FILE" \
        -p "$PROJECT" down -v --timeout 15 &>/dev/null || true
}
trap cleanup EXIT

echo "  Starting MLflow stack (first run builds the image)..."
if docker compose -f "$COMPOSE" --env-file "$ENV_FILE" \
        -p "$PROJECT" up -d --build 2>&1 | tail -3; then
    pass "docker compose up"
else
    fail "docker compose up"
    summary "Smoke"; exit 1
fi

# Load ports from env file
set -a; source "$ENV_FILE"; set +a

wait_http() {
    local url="$1" desc="$2" max="${3:-120}" elapsed=0
    while (( elapsed < max )); do
        curl -sf "$url" &>/dev/null && { pass "$desc"; return 0; }
        sleep 5; ((elapsed+=5))
    done
    fail "$desc (no response after ${max}s)"
}

wait_http "http://localhost:${MLFLOW_PORT:-5000}/health"              "MLflow /health"         120
wait_http "http://localhost:${MINIO_API_PORT:-9000}/minio/health/live" "MinIO S3 /health"       60
wait_http "http://localhost:${MINIO_CONSOLE_PORT:-9001}"               "MinIO Console reachable" 30

summary "Smoke"
