#!/usr/bin/env bash
# Assigns a unique port block to this deployment and writes per-service .env files.
#
# Usage:
#   ./scripts/generate-ports.sh            # assign ports for current $USER@$HOSTNAME
#   ./scripts/generate-ports.sh --show     # print assigned ports without rewriting
#   ./scripts/generate-ports.sh --test     # collision-test 20 simulated deployments
#   ./scripts/generate-ports.sh --force    # reassign even if ports already exist
#
# Port scheme:
#   Each deployment occupies a 20-port block in the range 20000-59999.
#   Slot N → ports 20000 + N*20  through  20000 + N*20 + 19
#   Slot is derived from a hash of USER@HOSTNAME, giving up to 2000 deployments.
#
#   Sub-offsets within each block:
#     +0  MLFLOW_PORT              +10 DAGSTER_PORT
#     +1  MLFLOW_POSTGRES_PORT     +11 DAGSTER_POSTGRES_PORT
#     +2  MLFLOW_MINIO_PORT        +12 EVIDENTLY_PORT
#     +3  MLFLOW_MINIO_CONSOLE_PORT +13 BENTOML_PORT
#     +4  DVC_MINIO_PORT           +14 GRAFANA_PORT
#     +5  DVC_MINIO_CONSOLE_PORT   +15 PROMETHEUS_PORT
#     +6  LABEL_STUDIO_PORT        +16 CADVISOR_PORT
#     +7  LABEL_STUDIO_POSTGRES_PORT +17 LABS_PORT
#     +8  JUPYTER_PORT
#     +9  (reserved)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SHOW=false
TEST_MODE=false
FORCE=false

for arg in "$@"; do
  case "$arg" in
    --show)  SHOW=true ;;
    --test)  TEST_MODE=true ;;
    --force) FORCE=true ;;
    --help|-h)
      echo "Usage: $0 [--show] [--test] [--force]"
      exit 0 ;;
  esac
done

# ── Collision test ────────────────────────────────────────────────────────────
if [[ "${TEST_MODE}" == "true" ]]; then
  echo "==> Collision test: 20 simulated deployments"
  declare -A seen
  all_ok=true
  for i in $(seq 1 20); do
    # Simulate different user@host hashes by using index directly as slot
    slot=$(( (i * 7 + 3) % 2000 ))          # spread across slot space
    base=$(( 20000 + slot * 20 ))
    echo -n "  Deployment $i  slot=$slot  ports $base-$(( base + 17 ))  "
    collision=false
    for offset in $(seq 0 17); do
      p=$(( base + offset ))
      if [[ -n "${seen[$p]+_}" ]]; then
        echo "COLLISION on port $p with deployment ${seen[$p]}"
        collision=true
        all_ok=false
        break
      fi
      seen[$p]=$i
    done
    [[ "${collision}" == "false" ]] && echo "OK"
  done
  if [[ "${all_ok}" == "true" ]]; then
    echo ""
    echo "  All 20 deployments have non-overlapping port sets. ✓"
  else
    echo ""
    echo "  FAIL: collision detected."
    exit 1
  fi
  exit 0
fi

# ── Derive slot from USER@HOSTNAME hash ───────────────────────────────────────
IDENTITY="${USER:-anonymous}@${HOSTNAME:-localhost}"
SLOT=$(( $(printf '%s' "${IDENTITY}" | cksum | awk '{print $1}') % 2000 ))
BASE=$(( 20000 + SLOT * 20 ))

declare -A PORTS=(
  [MLFLOW_PORT]=$(( BASE + 0 ))
  [MLFLOW_POSTGRES_PORT]=$(( BASE + 1 ))
  [MLFLOW_MINIO_PORT]=$(( BASE + 2 ))
  [MLFLOW_MINIO_CONSOLE_PORT]=$(( BASE + 3 ))
  [DVC_MINIO_PORT]=$(( BASE + 4 ))
  [DVC_MINIO_CONSOLE_PORT]=$(( BASE + 5 ))
  [LABEL_STUDIO_PORT]=$(( BASE + 6 ))
  [LABEL_STUDIO_POSTGRES_PORT]=$(( BASE + 7 ))
  [JUPYTER_PORT]=$(( BASE + 8 ))
  [DAGSTER_PORT]=$(( BASE + 10 ))
  [DAGSTER_POSTGRES_PORT]=$(( BASE + 11 ))
  [EVIDENTLY_PORT]=$(( BASE + 12 ))
  [BENTOML_PORT]=$(( BASE + 13 ))
  [GRAFANA_PORT]=$(( BASE + 14 ))
  [PROMETHEUS_PORT]=$(( BASE + 15 ))
  [CADVISOR_PORT]=$(( BASE + 16 ))
  [LABS_PORT]=$(( BASE + 17 ))
)

if [[ "${SHOW}" == "true" ]]; then
  echo "Deployment: ${IDENTITY}  slot=${SLOT}  base=${BASE}"
  echo ""
  for key in $(echo "${!PORTS[@]}" | tr ' ' '\n' | sort); do
    printf "  %-32s %s\n" "${key}" "${PORTS[$key]}"
  done
  exit 0
fi

# ── Write .env files ──────────────────────────────────────────────────────────
# Service-to-variable mapping
declare -A SVC_VARS=(
  [mlflow]="MLFLOW_PORT MLFLOW_POSTGRES_PORT MLFLOW_MINIO_PORT MLFLOW_MINIO_CONSOLE_PORT"
  [dvc]="DVC_MINIO_PORT DVC_MINIO_CONSOLE_PORT"
  [label-studio]="LABEL_STUDIO_PORT LABEL_STUDIO_POSTGRES_PORT"
  [jupyterlab]="JUPYTER_PORT"
  [dagster]="DAGSTER_PORT DAGSTER_POSTGRES_PORT"
  [evidently]="EVIDENTLY_PORT"
  [bentoml]="BENTOML_PORT"
  [monitoring]="GRAFANA_PORT PROMETHEUS_PORT CADVISOR_PORT"
  [labs]="LABS_PORT"
)

echo "==> Generating ports for ${IDENTITY}  (slot ${SLOT}, base ${BASE})"
echo ""

for svc in "${!SVC_VARS[@]}"; do
  env_file="${REPO_ROOT}/services/${svc}/.env"
  example_file="${env_file}.example"

  # Bootstrap .env from example if needed
  if [[ ! -f "${env_file}" ]] && [[ -f "${example_file}" ]]; then
    cp "${example_file}" "${env_file}"
  fi

  if [[ ! -f "${env_file}" ]]; then
    echo "  SKIP ${svc} — no .env file found"
    continue
  fi

  # Only write if --force or the PORT line still has the default value
  vars="${SVC_VARS[$svc]}"
  for var in $vars; do
    new_val="${PORTS[$var]}"
    if grep -q "^${var}=" "${env_file}"; then
      current=$(grep "^${var}=" "${env_file}" | cut -d= -f2)
      if [[ "${FORCE}" == "true" ]] || [[ "${current}" == "${new_val}" ]] || \
         ( [[ "${current}" -ge 1024 ]] && [[ "${current}" -le 9999 ]] ); then
        sed -i "s|^${var}=.*|${var}=${new_val}|" "${env_file}"
        printf "  %-12s  %-32s %s\n" "${svc}" "${var}" "${new_val}"
      fi
    else
      echo "${var}=${new_val}" >> "${env_file}"
      printf "  %-12s  %-32s %s\n" "${svc}" "${var}" "${new_val}"
    fi
  done
done

echo ""
echo "Done. Run './scripts/start.sh <service>' to start each service."
echo "Run './scripts/generate-ports.sh --show' to review assigned ports."
