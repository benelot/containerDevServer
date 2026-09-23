#!/usr/bin/env bash
# Usage: ./scripts/backup.sh [--dest DIR] [--services all|mlflow,dagster,...]
#   --dest    destination directory (default: ./backups)
#   --services comma-separated list, or "all" (default: all)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DEST="${REPO_ROOT}/backups"
SERVICES="all"

for arg in "$@"; do
  case "$arg" in
    --dest=*)    DEST="${arg#*=}" ;;
    --services=*) SERVICES="${arg#*=}" ;;
    --help|-h)
      echo "Usage: $0 [--dest=DIR] [--services=all|mlflow,dagster,...]"
      exit 0 ;;
  esac
done

TS=$(date '+%Y%m%d_%H%M%S')
BACKUP_DIR="${DEST}/${TS}"
mkdir -p "${BACKUP_DIR}"

# ── Helpers ───────────────────────────────────────────────────────────────────
want() { [[ "${SERVICES}" == "all" ]] || echo ",${SERVICES}," | grep -q ",${1},"; }

pg_dump_service() {
  local name="$1" container="$2" user="$3" db="$4"
  if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
    echo "  pg_dump ${name}..."
    docker exec "${container}" pg_dump -U "${user}" "${db}" \
      | gzip > "${BACKUP_DIR}/${name}_postgres.sql.gz"
    echo "  [ok] ${name}_postgres.sql.gz"
  else
    echo "  [skip] ${name}: container ${container} not running"
  fi
}

minio_mirror() {
  local name="$1" endpoint="$2" user="$3" pass="$4" bucket="$5"
  local dest="${BACKUP_DIR}/${name}_minio"
  mkdir -p "${dest}"
  if curl -sf "${endpoint}/minio/health/live" > /dev/null 2>&1; then
    echo "  mc mirror ${name} (${bucket})..."
    docker run --rm --network host \
      -e MC_HOST_src="http://${user}:${pass}@${endpoint#http://}" \
      -v "${dest}:/dest" \
      minio/mc mirror "src/${bucket}" /dest 2>&1 | tail -5
    echo "  [ok] ${name}_minio/${bucket}"
  else
    echo "  [skip] ${name}: MinIO not reachable at ${endpoint}"
  fi
}

volume_backup() {
  local name="$1" volume="$2"
  echo "  volume ${volume}..."
  docker run --rm \
    -v "${volume}:/data:ro" \
    -v "${BACKUP_DIR}:/backup" \
    alpine tar czf "/backup/${name}_volume.tar.gz" -C /data .
  echo "  [ok] ${name}_volume.tar.gz"
}

# ── MLflow ────────────────────────────────────────────────────────────────────
if want mlflow; then
  echo "── MLflow ─────────────────────────"
  ENV="${REPO_ROOT}/services/mlflow/.env"
  [[ -f "${ENV}" ]] || ENV="${REPO_ROOT}/services/mlflow/.env.example"
  # shellcheck source=/dev/null
  source <(grep -E '^[A-Z_]+=' "${ENV}")
  pg_dump_service mlflow "mlflow-postgres-1" "${POSTGRES_USER:-mlflow}" "${POSTGRES_DB:-mlflow}"
  minio_mirror mlflow "http://localhost:${MINIO_API_PORT:-9000}" \
    "${MINIO_ROOT_USER:-minioadmin}" "${MINIO_ROOT_PASSWORD:-minioadmin_secret}" \
    "${MINIO_BUCKET:-mlflow}"
fi

# ── Label Studio ──────────────────────────────────────────────────────────────
if want label-studio; then
  echo "── Label Studio ───────────────────"
  ENV="${REPO_ROOT}/services/label-studio/.env"
  [[ -f "${ENV}" ]] || ENV="${REPO_ROOT}/services/label-studio/.env.example"
  source <(grep -E '^[A-Z_]+=' "${ENV}")
  pg_dump_service label-studio "label-studio-postgres-1" \
    "${POSTGRES_USER:-labelstudio}" "${POSTGRES_DB:-labelstudio}"
fi

# ── Dagster ───────────────────────────────────────────────────────────────────
if want dagster; then
  echo "── Dagster ────────────────────────"
  ENV="${REPO_ROOT}/services/dagster/.env"
  [[ -f "${ENV}" ]] || ENV="${REPO_ROOT}/services/dagster/.env.example"
  source <(grep -E '^[A-Z_]+=' "${ENV}")
  pg_dump_service dagster "dagster-dagster-postgres-1" \
    "${POSTGRES_USER:-dagster}" "${POSTGRES_DB:-dagster}"
fi

# ── DVC MinIO ─────────────────────────────────────────────────────────────────
if want dvc; then
  echo "── DVC ────────────────────────────"
  ENV="${REPO_ROOT}/services/dvc/.env"
  [[ -f "${ENV}" ]] || ENV="${REPO_ROOT}/services/dvc/.env.example"
  source <(grep -E '^[A-Z_]+=' "${ENV}")
  minio_mirror dvc "http://localhost:${MINIO_API_PORT:-9010}" \
    "${MINIO_ROOT_USER:-minioadmin}" "${MINIO_ROOT_PASSWORD:-minioadmin_secret}" \
    "${MINIO_BUCKET:-dvc-cache}"
fi

# ── Evidently workspace volume ────────────────────────────────────────────────
if want evidently; then
  echo "── Evidently ──────────────────────"
  if docker volume ls --format '{{.Name}}' | grep -q evidently_workspace; then
    volume_backup evidently evidently-stack_evidently_workspace
  else
    echo "  [skip] evidently: volume not found"
  fi
fi

# ── Pack everything into a single archive ─────────────────────────────────────
echo ""
echo "── Packing archive ────────────────"
ARCHIVE="${DEST}/${TS}.tar.gz"
tar czf "${ARCHIVE}" -C "${DEST}" "${TS}"
rm -rf "${BACKUP_DIR}"

SIZE=$(du -sh "${ARCHIVE}" | cut -f1)
echo ""
echo "============================================================"
echo "  Backup complete: ${ARCHIVE}  (${SIZE})"
echo "  Timestamp: ${TS}"
echo "============================================================"
