# Container Dev Server

## Repo layout

```
ansible/           Ansible playbook to provision Docker on a fresh Ubuntu host
  roles/docker/          Install Docker CE + Compose plugin
  roles/docker_config/   Configure daemon.json, docker group membership
  inventory/hosts.yml    Target hosts and variable overrides

services/          One directory per stack; each is independent
  mlflow/          MLflow + PostgreSQL + MinIO (experiment tracking, model registry)
  dvc/             MinIO S3 remote for DVC artifact cache
  label-studio/    Label Studio + PostgreSQL (data annotation)
  jupyterlab/      JupyterLab (datascience-notebook image)
  dagster/         Dagster webserver + daemon + PostgreSQL (pipeline orchestration)
  evidently/       Evidently UI (data drift and model monitoring)
  bentoml/         BentoML REST serving (loads Production model from MLflow)

scripts/
  start.sh         Start/stop any stack; --random assigns unused ports

tests/
  run_tests.sh     Test runner (structure, YAML, env coverage, Ansible, Compose)
  test_smoke.sh    Integration smoke test (INTEGRATION=1 required)
```

## Key conventions

- Every service has a `docker-compose.yml` and `.env.example`.
- All ports are `${VAR_NAME:-default}` -- override in `.env`, or run with `--random`.
- Default ports are offset per service so stacks can run simultaneously:
  MLflow 5000/5432/9000/9001, DVC 9010/9011, Label Studio 8080/5433, Jupyter 8888,
  Dagster 3000/5434, Evidently 8001, BentoML 3001.
- The `start.sh` script copies `.env.example` to `.env` on first run.
- Adding a new service: create `services/<name>/docker-compose.yml` and `.env.example`,
  add a case block in `scripts/start.sh`, add `check_file` lines in `tests/test_structure.sh`.

## Running tests

```bash
bash tests/run_tests.sh                  # static checks only
INTEGRATION=1 bash tests/run_tests.sh   # also starts MLflow, checks HTTP, tears down
```

## Ansible provisioning

```bash
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbook.yml
```

Override `docker_data_root` and `docker_users` in `inventory/hosts.yml`.

## Important variables

| Variable | Role | Default |
|---|---|---|
| `docker_data_root` | `docker_config` | `/var/lib/docker` |
| `docker_users` | `docker_config` | `[]` |
| `docker_log_max_size` | `docker_config` | `10m` |
