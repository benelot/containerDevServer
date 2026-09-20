# JupyterLab

Interactive notebook environment for exploration, prototyping, and stakeholder reporting across all CRISP-DM phases.

## CRISP-DM role

| Phase | Contribution |
|---|---|
| Business Understanding | Document the problem definition, success criteria, and constraints before touching data |
| Data Understanding | Explore distributions, visualise samples, identify anomalies |
| Data Preparation | Prototype cleaning and feature engineering steps before committing them to the Dagster pipeline |
| Modelling | Iterate quickly on architecture and hyperparameters; every run logged to MLflow |
| Evaluation | Produce confusion matrices, t-SNE projections, and quality reports for review |

## Image

Uses `jupyter/datascience-notebook`, which ships Python, R, and Julia kernels along with a broad set of scientific libraries (NumPy, pandas, scikit-learn, matplotlib, seaborn, and more). Additional packages can be installed inside a running container with `pip install` or `conda install` without rebuilding the image.

## Key configuration choices

**Host networking for MLflow connectivity.** On Linux, `host.docker.internal` is not automatically available. The compose file adds `host.docker.internal:host-gateway` as an extra host, so notebooks can reach the MLflow server at `http://host.docker.internal:5000` the same way macOS clients do. This avoids hard-coding the host IP in notebooks.

**Root user.** The container runs as root so that `pip install` and `apt install` work without `sudo` during interactive sessions. This is appropriate for a single-user local development environment; adjust for shared or production deployments.

**Bind-mounted notebooks.** The repo's `notebooks/` directory is mounted into the container so all notebooks are saved directly to disk and can be committed to Git.

## Quickstart

```bash
./scripts/start.sh jupyterlab
# http://localhost:8888/?token=<JUPYTER_TOKEN from .env>
```

MLflow is pre-configured via environment variables:

```python
import mlflow, os
mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
# → "http://host.docker.internal:5000"
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `JUPYTER_PORT` | `8888` | JupyterLab port |
| `JUPYTER_TOKEN` | `changeme` | Notebook server token — change before exposing the port |
| `MLFLOW_TRACKING_URI` | `http://host.docker.internal:5000` | MLflow server URL visible from inside the container |
| `MLFLOW_S3_ENDPOINT_URL` | `http://host.docker.internal:9000` | MinIO endpoint for artifact uploads |
