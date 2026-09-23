# Container Dev Server

A self-hosted data science development environment built on Docker Compose and provisioned with Ansible. The stack covers the complete machine learning lifecycle — from raw data through annotation, pipeline orchestration, experiment tracking, model serving, and production monitoring.

---

## CRISP-DM methodology

CRISP-DM (Cross-Industry Standard Process for Data Mining) describes the full lifecycle of a data science project as six iterative phases. Progress is rarely linear; findings in evaluation regularly send a team back to data preparation, and drift detected in production triggers a new data collection and retraining cycle.

```
   Business          Data             Data
  Understanding  Understanding    Preparation
       |               |               |
       v               v               v
  +-----------+  +-----------+  +-----------+
  | Define    |  | Explore & |  | Clean,    |
  | goal &    |  | describe  |  | transform,|
  | success   |  | the data  |  | engineer  |
  | criteria  |  |           |  | features  |
  +-----------+  +-----------+  +-----------+
       ^                               |
       |                               v
  +-----------+  +-----------+  +-----------+
  | Deploy &  |  | Evaluate  |  | Model     |
  | monitor   |  | against   |  | Select,   |
  | in prod   |  | business  |  | train &   |
  |           |  | criteria  |  | tune      |
  +-----------+  +-----------+  +-----------+
   Deployment     Evaluation      Modelling
       ^               |
       +---------------+  (monitor → re-label → retrain)
```

### How each service maps to the cycle

| Phase | Primary tools | Role |
|---|---|---|
| Business Understanding | JupyterLab | Define the problem and success criteria before touching data |
| Data Understanding | JupyterLab, Label Studio | Explore, visualise, and annotate raw data; identify issues early |
| Data Preparation | JupyterLab, DVC, Dagster + Pandera | Clean and transform; version every dataset; validate schema before training |
| Modelling | JupyterLab, Dagster, MLflow | Iterate on architecture and hyperparameters; every run tracked automatically |
| Evaluation | MLflow, Dagster + DeepChecks + Evidently | Compare experiments; check data and model quality; surface results to stakeholders |
| Deployment | MLflow Model Registry, BentoML, Dagster, Evidently | Register and stage models; serve via REST API; schedule retraining; monitor for drift |

The feedback loop that closes the cycle: Evidently surfaces drift in production data flowing through BentoML. New samples are sent to Label Studio for re-labeling. The Dagster pipeline re-runs with the updated labeled dataset. A new model is registered in MLflow. BentoML loads the new Production model on restart.

---

## Services at a glance

| Service | Default URL | Purpose |
|---|---|---|
| **JupyterLab** | http://host:8888 | Interactive exploration and prototyping |
| **MLflow** | http://host:5000 | Experiment tracking and model registry |
| **DVC remote** | MinIO at host:9010 | Dataset and artifact versioning |
| **Label Studio** | http://host:8080 | Data annotation |
| **Dagster** | http://host:3000 | Pipeline orchestration |
| **Evidently** | http://host:8001 | Data drift and model monitoring UI |
| **BentoML** | http://host:3001 | Model serving (REST API + Swagger UI) |
| **Monitoring** | Grafana http://host:3002 | Service health, CPU/RAM/GPU dashboards |

Each service has its own README in `services/<name>/README.md` with configuration details and its CRISP-DM role.

---

## 1. Provision the host

```bash
# Edit ansible/inventory/hosts.yml first:
#   docker_data_root: path to your data disk  (e.g. /data/docker)
#   docker_users:     OS users that need Docker access

ansible-playbook -i ansible/inventory/hosts.yml ansible/playbook.yml
```

After the playbook completes, listed users can run `docker` without sudo (log out and back in first).

---

## 2. Start a service

```bash
# First run copies .env.example → .env automatically
./scripts/start.sh jupyterlab
./scripts/start.sh mlflow
./scripts/start.sh dvc
./scripts/start.sh label-studio
./scripts/start.sh dagster
./scripts/start.sh evidently
./scripts/start.sh bentoml
./scripts/start.sh monitoring

# Assign random available ports (written to .env, useful on shared hosts)
./scripts/start.sh mlflow --random

# Stop a stack
./scripts/start.sh mlflow --stop
```

The script prints service URLs and client configuration after startup.

---

## 3. Run a full CRISP-DM example

The repository includes two notebooks that walk through the complete cycle on the MNIST 1D dataset (40-point 1D digit sequences representing handwritten digits 0–9).

```bash
# Generate or regenerate the notebooks from source scripts
python3 scripts/generate_notebooks.py
python3 scripts/generate_data_quality_notebook.py
```

| Notebook | What it covers |
|---|---|
| `notebooks/mnist1d_crisp_dm.ipynb` | Full CRISP-DM cycle: data exploration, Conv1D training with MLflow, confusion matrix, t-SNE, model registration |
| `notebooks/data_quality.ipynb` | Data validation with Pandera, DeepChecks, Evidently, and Pointblank |

Open either notebook in JupyterLab once the MLflow and JupyterLab stacks are running.

---

## Services

### JupyterLab (`services/jupyterlab/`)

Interactive workspace for all exploratory and prototyping work. Runs `jupyter/datascience-notebook` with Python, R, and Julia kernels. The repo's `notebooks/` directory is bind-mounted so notebooks are saved directly to Git. MLflow connection details are injected as environment variables so experiment logging works out of the box.

```bash
./scripts/start.sh jupyterlab
# http://localhost:8888/?token=<JUPYTER_TOKEN from .env>
```

### MLflow (`services/mlflow/`)

Experiment tracker, artifact store, and model registry. Uses PostgreSQL for run metadata — supporting concurrent writers from both notebooks and the Dagster pipeline — and MinIO as an S3-compatible artifact backend. The `--serve-artifacts` flag means clients never need direct MinIO credentials; all artifact traffic proxies through the MLflow server.

```bash
./scripts/start.sh mlflow

import mlflow
mlflow.set_tracking_uri("http://localhost:5000")
```

| Endpoint | Port |
|---|---|
| MLflow UI | 5000 |
| MinIO S3 API | 9000 |
| MinIO Console | 9001 |
| PostgreSQL | 5432 |

### DVC remote (`services/dvc/`)

MinIO S3 remote for dataset versioning. A dedicated MinIO instance (ports 9010/9011) keeps DVC data isolated from MLflow artifacts. Switching to a real S3 bucket later requires changing only the endpoint URL in your DVC remote configuration.

```bash
./scripts/start.sh dvc

dvc remote add -d myremote s3://dvc-cache
dvc remote modify myremote endpointurl http://localhost:9010
dvc remote modify myremote access_key_id minioadmin
dvc remote modify myremote secret_access_key minioadmin_secret
```

### Label Studio (`services/label-studio/`)

Web-based data annotation tool. PostgreSQL backend on port 5433. Annotated exports can be versioned immediately with DVC and fed into the Dagster pipeline.

```bash
./scripts/start.sh label-studio
# http://localhost:8080  —  login: admin@example.com / changeme (set in .env)
```

### Dagster (`services/dagster/`)

Pipeline orchestrator built on software-defined assets. The included `mnist1d_full_pipeline` runs four assets in sequence: download raw data, validate with Pandera, generate quality reports with Evidently and DeepChecks, and train a Conv1D model with all metrics logged to MLflow.

```bash
./scripts/start.sh dagster
# http://localhost:3000  —  Assets > Materialize All, or Jobs > mnist1d_full_pipeline
```

**Data quality libraries** (installed in the Dagster image):

- **Pandera** — schema validation on DataFrames; checks column types, value ranges, and allowed labels at the data ingestion boundary
- **DeepChecks** — ML-specific integrity checks: train/test distribution, feature leakage, class imbalance
- **Evidently** — drift and quality reports that feed into the monitoring UI; bridges pipeline validation and post-deployment monitoring

### BentoML (`services/bentoml/`)

Model serving layer. Loads the `Production` model from the MLflow registry on startup and exposes a typed REST API with automatic Swagger documentation. If no Production model is registered yet the service starts in degraded mode, returning HTTP 503 on `/predict` with an explanatory message. This makes startup order safe: the container can launch alongside the rest of the stack and become fully operational once a model is promoted.

```bash
./scripts/start.sh bentoml
# http://localhost:3001       — Swagger UI
# http://localhost:3001/health — model load status

curl -X POST http://localhost:3001/predict \
  -H "Content-Type: application/json" \
  -d '[[0.1, -0.2, 0.3, ...]]'
# {"predictions": [3], "probabilities": [[0.01, ..., 0.92, ...]]}
```

Change `MLFLOW_MODEL_NAME` or `MLFLOW_MODEL_STAGE` in `.env` to serve a different model or stage without touching any code.

### Evidently (`services/evidently/`)

Monitoring UI for data drift and model performance over time. Receives JSON snapshots pushed from Python code in notebooks or the Dagster pipeline and renders them as interactive dashboards. When drift is detected, new data can be routed to Label Studio for re-labeling, closing the CRISP-DM feedback loop.

```bash
./scripts/start.sh evidently
# http://localhost:8001

from evidently.ui.workspace import Workspace
ws = Workspace(url="http://localhost:8001")
ws.add_run(project.id, report)
```

### Monitoring (`services/monitoring/`)

Prometheus + Grafana stack with pre-built dashboards for hardware metrics and service health. Includes a per-service health dashboard with UP/DOWN status for all services, host CPU/RAM/disk, per-container CPU/RAM from cAdvisor, and optional NVIDIA GPU metrics via dcgm_exporter.

```bash
./scripts/start.sh monitoring
# http://localhost:3002  — Grafana (admin / admin by default)
# http://localhost:9090  — Prometheus
```

GPU metrics are opt-in. On NVIDIA hosts, start with:

```bash
docker compose --profile gpu up -d
```

---

## Backup

```bash
# Backup all services to ./backups/<timestamp>/
./scripts/backup.sh

# Backup specific services
./scripts/backup.sh --services mlflow,label-studio

# Backup to a custom destination
./scripts/backup.sh --dest /mnt/nas/backups
```

The backup script captures PostgreSQL databases with `pg_dump`, MinIO buckets with `mc mirror`, and Docker volumes as compressed tarballs.

---

## Running tests

```bash
bash tests/run_tests.sh                  # structure, YAML, .env coverage, Compose validation
INTEGRATION=1 bash tests/run_tests.sh   # also starts MLflow and checks live HTTP endpoints
```

---

## Configuration

Each service reads from `services/<name>/.env`. The start script copies `.env.example` to `.env` on first run. All ports use `${VAR_NAME:-default}` so defaults work with no `.env` and all stacks can run simultaneously without conflict.

---

## Multi-user setup

Each user on a shared machine runs their own fully isolated stack — no administrator involvement needed. Clone the repo, run two commands, and start the labs.

```bash
# 1. Assign your personal port set (run once; safe to re-run)
bash scripts/generate-ports.sh

# 2. Start whatever service you need
./scripts/start.sh mlflow
```

That is the entire onboarding. The two isolation mechanisms work automatically:

**Port isolation** — `generate-ports.sh` hashes your `USER@HOSTNAME` into a slot (0–1999) and maps 17 service ports to a unique block starting at `20000 + slot × 20`. No two slots share a port. The assignments are written to each service's `.env` file and reloaded on every `start.sh` call.

**Container isolation** — `start.sh` passes `--project-name "${USER}-${SERVICE}"` to every Docker Compose command. All containers, networks, and volumes are prefixed with your username. Two users running `./scripts/start.sh mlflow` produce completely separate stacks: `alice-mlflow-mlflow-1` and `bob-mlflow-mlflow-1`, each with their own PostgreSQL data and MinIO buckets.

The interactive labs at port `LABS_PORT` (from your generated `.env`) walk through the full CRISP-DM workflow and automatically show the correct port numbers for your personal setup.

---

## Ansible role variables

| Variable | Role | Default | Description |
|---|---|---|---|
| `docker_data_root` | `docker_config` | `/var/lib/docker` | Docker storage path |
| `docker_users` | `docker_config` | `[]` | Users added to the docker group |
| `docker_log_max_size` | `docker_config` | `10m` | Max per-container log file size |
| `docker_log_max_file` | `docker_config` | `3` | Number of log files to rotate |
