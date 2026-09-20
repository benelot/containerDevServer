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
    pipelines/mnist1d_pipeline.py  Four-asset CRISP-DM example pipeline
  evidently/       Evidently UI (data drift and model monitoring)
  bentoml/         BentoML REST serving (loads Production model from MLflow)
    service.py     BentoML 1.x @bentoml.service class; loads from MLflow on startup
  monitoring/      Prometheus + Grafana + node_exporter + cAdvisor + blackbox probes
  labs/            Hugo + FastAPI interactive labs; port 3003
    hugo.toml            Hugo site config (relearn theme, taskList extension)
    content/             8 labs (00-introduction through 08-monitoring)
    layouts/shortcodes/  {{< port >}} and {{< svcurl >}} inject live port values
    scripts/generate_ports_data.py  Reads env vars → data/ports.yaml at container start

scripts/
  generate-ports.sh    Assign deterministic non-colliding port slots per user@host
  start.sh         Start/stop any stack; --random assigns unused ports
  backup.sh        Dump PostgreSQL DBs, mirror MinIO buckets, tar Docker volumes
  generate_notebooks.py             Regenerate notebooks/mnist1d_crisp_dm.ipynb
  generate_data_quality_notebook.py Regenerate notebooks/data_quality.ipynb

tests/
  run_tests.sh     Test runner (structure, YAML, env coverage, Ansible, Compose)
  test_smoke.sh    Integration smoke test (INTEGRATION=1 required)

notebooks/
  mnist1d_crisp_dm.ipynb   Full CRISP-DM cycle on MNIST 1D; do not edit directly
  data_quality.ipynb       Pandera / DeepChecks / Evidently / Pointblank; do not edit directly
```

## Key conventions

- Every service has a `docker-compose.yml` and `.env.example`.
- All ports are `${VAR_NAME:-default}` — override in `.env`, or run with `--random`.
- Default ports are offset per service so stacks can run simultaneously:
  MLflow 5000/5432/9000/9001, DVC 9010/9011, Label Studio 8080/5433, Jupyter 8888,
  Dagster 3000/5434, Evidently 8001, BentoML 3001,
  Monitoring: Grafana 3002, Prometheus 9090, cAdvisor 8082, Labs 3003.
- The `start.sh` script copies `.env.example` to `.env` on first run.
- Notebooks are generated files — edit the generator scripts, not the `.ipynb` files.
- Adding a new service: create `services/<name>/docker-compose.yml` and `.env.example`,
  add a case block in `scripts/start.sh`, add `check_file` lines in `tests/test_structure.sh`.

## BentoML service

Uses BentoML 1.x API: `@bentoml.service` class decorator, `@bentoml.api` method decorators.
The CMD in the Dockerfile is `bentoml serve service:Mnist1DClassifier`.
Do not use the BentoML 0.x `bentoml.Runner`, `bentoml.Service()`, or `bentoml.io` API — those
were removed in 1.x.

## Dagster pipeline

The registered model name is `mnist1d-conv1d` in both the pipeline and BentoML. Changing it
in one place requires changing it in the other, or the serving layer will not find the model.

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
