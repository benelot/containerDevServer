# MLflow

Experiment tracker, artifact store, and model registry for the CRISP-DM Modelling and Evaluation phases.

## CRISP-DM role

| Phase | Contribution |
|---|---|
| Modelling | Every training run logs parameters, metrics, and artifacts automatically |
| Evaluation | Compare runs side-by-side in the UI; pick the best model for promotion |
| Deployment | Model Registry stores versioned models with lifecycle stages (Staging, Production) |

## Architecture

```
Client (notebook / Dagster)
        │  HTTP
        ▼
  MLflow server  ──► PostgreSQL  (run metadata, parameters, metrics)
        │
        └──► MinIO (S3-compatible)  (artifacts: model files, HTML reports, plots)
```

The `--serve-artifacts` flag means all artifact traffic proxies through the MLflow server. Clients never need direct MinIO credentials or network access to MinIO.

## Services

| Container | Port | Purpose |
|---|---|---|
| `mlflow` | 5000 | MLflow tracking server + artifact proxy |
| `mlflow-db` | 5432 | PostgreSQL — run metadata |
| `mlflow-minio` | 9000 | MinIO S3 API — artifact storage |
| `mlflow-minio` | 9001 | MinIO web console |

## Quickstart

```bash
./scripts/start.sh mlflow
# http://localhost:5000
```

Connect from Python:

```python
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("my-experiment")

with mlflow.start_run():
    mlflow.log_param("lr", 0.001)
    mlflow.log_metric("val_acc", 0.94)
    mlflow.pytorch.log_model(model, "model", registered_model_name="my-model")
```

## Model Registry

After training, promote a model in the UI or from Python:

```python
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="mnist1d-conv1d",
    version=1,
    stage="Production",
)
```

BentoML picks up the new Production model on next restart.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `MLFLOW_PORT` | `5000` | MLflow server port |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `MINIO_PORT` | `9000` | MinIO S3 API port |
| `MINIO_CONSOLE_PORT` | `9001` | MinIO web console port |
| `POSTGRES_USER` | `mlflow` | Database user |
| `POSTGRES_PASSWORD` | `mlflow_secret` | Database password |
| `MINIO_ROOT_USER` | `minioadmin` | MinIO access key |
| `MINIO_ROOT_PASSWORD` | `minioadmin_secret` | MinIO secret key |
