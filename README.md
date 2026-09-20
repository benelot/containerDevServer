# Container Dev Server

A self-hosted data science development environment built on Docker Compose and provisioned with Ansible. Every service in this stack maps to a specific phase of the CRISP-DM methodology, forming a complete local ML platform.

## Prerequisites

- Ubuntu 22.04+ (Ansible target)
- Ansible on the control machine
- Docker + Docker Compose plugin (installed by the playbook)

---

## CRISP-DM and this stack

**CRISP-DM** (Cross-Industry Standard Process for Data Mining) is a methodology that describes the full lifecycle of a data science project as six iterative phases. The cycle is not linear -- findings in a later phase regularly send you back to an earlier one.

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
       +---------------+  (monitor -> re-label -> retrain)
```

### How each service maps to the cycle

| Phase | Primary tools | Role |
|---|---|---|
| Business Understanding | JupyterLab | Write down the problem definition and success criteria before touching data |
| Data Understanding | JupyterLab, Label Studio | Explore, visualise, and annotate raw data; identify issues early |
| Data Preparation | JupyterLab, DVC, Dagster + Pandera | Clean and transform; version every dataset; validate schema before it reaches training |
| Modelling | JupyterLab, Dagster, MLflow | Iterate on architecture and hyperparameters; every run is tracked automatically |
| Evaluation | MLflow, Dagster + DeepChecks, Evidently | Compare experiments; check data and model quality; surface results to stakeholders |
| Deployment | MLflow Model Registry, Dagster, Evidently | Register and stage models; schedule retraining; monitor production data for drift |

The feedback loop that closes the cycle is: Evidently detects drift in production data -> new samples are sent to Label Studio for re-labeling -> the Dagster pipeline re-runs with the updated labeled dataset -> a new model is registered in MLflow.

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

Each service has its own README in `services/<name>/README.md` with configuration details and a full CRISP-DM role description.

---

## 1. Provision the host

```bash
# Edit ansible/inventory/hosts.yml first:
#   docker_data_root: path to your data disk  (e.g. /data/docker)
#   docker_users:     OS users that need Docker access

ansible-playbook -i ansible/inventory/hosts.yml ansible/playbook.yml
```

After this, listed users can run `docker` without sudo (log out and back in).

---

## 2. Start a service

```bash
# First run copies .env.example -> .env automatically
./scripts/start.sh jupyterlab
./scripts/start.sh mlflow
./scripts/start.sh dvc
./scripts/start.sh label-studio
./scripts/start.sh dagster
./scripts/start.sh evidently

# Assign random available ports (written to .env, useful on shared hosts)
./scripts/start.sh mlflow --random

# Stop a stack
./scripts/start.sh mlflow --stop
```

The script prints service URLs and client configuration after startup.

---

## 3. Run a full CRISP-DM example

The repository includes two notebooks that walk through the complete cycle on the MNIST 1D dataset (40-point 1D digit sequences).

```bash
# Generate or regenerate the notebooks from source scripts:
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

Interactive workspace for all exploratory and prototyping work. Runs `jupyter/datascience-notebook` (Python, R, Julia). The repo's `notebooks/` directory is bind-mounted so notebooks are saved directly to Git. MLflow connection details are injected as environment variables so logging works out of the box.

```bash
./scripts/start.sh jupyterlab
# http://localhost:8888/?token=<JUPYTER_TOKEN from .env>
```

### MLflow (`services/mlflow/`)

Experiment tracker, artifact store, and model registry. Uses PostgreSQL for run metadata (supports concurrent writers) and MinIO as an S3-compatible artifact backend. The `--serve-artifacts` flag means clients never need direct MinIO credentials.

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

MinIO S3 remote for dataset versioning. A separate MinIO instance (ports 9010/9011) keeps DVC data isolated from MLflow artifacts. Switching to a real S3 bucket later requires changing only the endpoint URL.

```bash
./scripts/start.sh dvc

dvc remote add -d myremote s3://dvc-cache
dvc remote modify myremote endpointurl http://localhost:9010
dvc remote modify myremote access_key_id minioadmin
dvc remote modify myremote secret_access_key minioadmin_secret
```

### Label Studio (`services/label-studio/`)

Web-based data annotation tool. PostgreSQL backend on port 5433 (offset from MLflow's 5432). Annotated exports can be versioned immediately with DVC and fed into the Dagster pipeline.

```bash
./scripts/start.sh label-studio
# http://localhost:8080  --  login: admin@example.com / changeme (set in .env)
```

### Dagster (`services/dagster/`)

Pipeline orchestrator built on software-defined assets. The included `mnist1d_full_pipeline` runs four assets in sequence: download raw data, validate with Pandera, generate quality reports with Evidently and DeepChecks, and train a Conv1D model with all metrics logged to MLflow.

```bash
./scripts/start.sh dagster
# http://localhost:3000  --  Assets > Materialize All, or Jobs > mnist1d_full_pipeline
```

**Data quality libraries** (installed in the Dagster image):

- **Pandera** -- schema validation on DataFrames; checks column types, value ranges, and allowed labels at the data ingestion boundary
- **DeepChecks** -- ML-specific integrity checks: train/test distribution, feature leakage, class imbalance
- **Evidently** -- drift and quality reports that feed into the monitoring UI; bridges pipeline validation and post-deployment monitoring
- **Pointblank** -- interactive HTML validation reports for stakeholder-facing data quality evidence

Great Expectations was evaluated but excluded. Pandera covers the same DataFrame validation use case with a cleaner API; the GX enterprise governance features are not needed at this scale.

### Evidently (`services/evidently/`)

Monitoring UI for data drift and model performance over time. Receives JSON snapshots pushed from Python code (notebooks or the Dagster pipeline) and renders them as interactive dashboards. Closing the CRISP-DM loop: when drift is detected, new data flows back to Label Studio for re-labeling.

```bash
./scripts/start.sh evidently
# http://localhost:8001

from evidently.ui.workspace import Workspace
ws = Workspace("http://localhost:8001")
ws.add_run(project.id, report)
```

---

## Configuration

Each service reads from `services/<name>/.env`. The start script copies `.env.example` to `.env` on first run. All ports follow `${VAR_NAME:-default}` so defaults work with no `.env` and all stacks can run simultaneously.

---

## Running tests

```bash
bash tests/run_tests.sh                  # structure, YAML, .env coverage, Compose validation
INTEGRATION=1 bash tests/run_tests.sh   # also starts MLflow and checks live HTTP endpoints
```

---

## Ansible role variables

| Variable | Role | Default | Description |
|---|---|---|---|
| `docker_data_root` | `docker_config` | `/var/lib/docker` | Docker storage path |
| `docker_users` | `docker_config` | `[]` | Users added to the docker group |
| `docker_log_max_size` | `docker_config` | `10m` | Max per-container log file size |
| `docker_log_max_file` | `docker_config` | `3` | Number of log files to rotate |
