# Container Dev Server

A self-hosted data science development environment built on Docker Compose, provisioned with Ansible.

## Prerequisites

- Ubuntu 22.04+ (Ansible target)
- Ansible on the control machine
- Docker + Docker Compose plugin (installed by the playbook)

---

## 1. Provision the host

```bash
# Edit ansible/inventory/hosts.yml first:
#   - Set docker_data_root to your data disk (e.g. /data/docker)
#   - Set docker_users to the OS users that need Docker access

ansible-playbook -i ansible/inventory/hosts.yml ansible/playbook.yml
```

After this, listed users can run `docker` without sudo (log out and back in to refresh group membership).

---

## 2. Start a service

```bash
# First run copies .env.example -> .env automatically
./scripts/start.sh mlflow
./scripts/start.sh dvc
./scripts/start.sh label-studio
./scripts/start.sh jupyterlab

# Assign random available ports (written to .env)
./scripts/start.sh mlflow --random

# Stop a stack
./scripts/start.sh mlflow --stop
```

The script prints all service URLs and client config after startup.

---

## Services

### MLflow (`services/mlflow/`)

Full MLflow tracking server with PostgreSQL backend and MinIO artifact store.

| Service | Default URL |
|---|---|
| MLflow Tracking UI | http://host:5000 |
| MinIO Console | http://host:9001 |
| MinIO S3 API | http://host:9000 |
| PostgreSQL | host:5432 |

Python client setup:
```python
import mlflow
mlflow.set_tracking_uri("http://host:5000")
```

### DVC remote cache (`services/dvc/`)

MinIO S3 remote for [DVC](https://dvc.org) artifact and data versioning.

After starting, run once in your DVC repo:
```bash
dvc remote add -d myremote s3://dvc-cache
dvc remote modify myremote endpointurl http://host:9010
dvc remote modify myremote access_key_id minioadmin
dvc remote modify myremote secret_access_key minioadmin_secret
```

### Label Studio (`services/label-studio/`)

[Label Studio](https://labelstud.io) data annotation tool with PostgreSQL backend.

| Service | Default URL |
|---|---|
| Label Studio UI | http://host:8080 |
| PostgreSQL | host:5433 |

Default login: `admin@example.com` / `changeme` (change in `.env`).

### JupyterLab (`services/jupyterlab/`)

[JupyterLab](https://jupyterlab.readthedocs.io) with Python, R, and Julia kernels
(`jupyter/datascience-notebook`).

| Service | Default URL |
|---|---|
| JupyterLab | http://host:8888/?token=changeme |

Notebooks persist in a Docker volume (`workspace`). Change `JUPYTER_IMAGE` in `.env`
to `jupyter/minimal-notebook` for a lighter image without R/Julia.

---

## Configuration

Each service reads from `services/<name>/.env`. Copy `.env.example` to `.env` and edit
before starting (the start script does the copy automatically on first run).

All port variables follow the pattern `${VAR_NAME:-default}` in the Compose files,
so the defaults work without any `.env` and the stacks can run side by side.

---

## Running tests

```bash
bash tests/run_tests.sh                  # file structure, YAML, .env coverage, Ansible/Compose validation
INTEGRATION=1 bash tests/run_tests.sh   # also starts MLflow stack and checks live HTTP endpoints
```

---

## Ansible role variables

| Variable | Role | Default | Description |
|---|---|---|---|
| `docker_data_root` | `docker_config` | `/var/lib/docker` | Docker storage path |
| `docker_users` | `docker_config` | `[]` | Users added to the docker group |
| `docker_log_max_size` | `docker_config` | `10m` | Max per-container log file size |
| `docker_log_max_file` | `docker_config` | `3` | Number of log files to rotate |
