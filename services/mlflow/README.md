# MLflow

## What it does

MLflow is an open-source platform for managing the machine learning lifecycle. It provides:

- **Experiment tracking** -- log parameters, metrics, and tags for every run
- **Artifact storage** -- save models, plots, and data files alongside each run
- **Model Registry** -- version, stage (Staging/Production), and annotate trained models
- **Model serving** -- optional REST endpoint for registered models

## Architecture in this stack

```
mlflow-server  <-- tracking API + artifact proxy
    |
    +-- PostgreSQL  (run metadata: params, metrics, tags)
    +-- MinIO       (artifact blobs: model files, images, reports)
```

The MLflow server runs with `--serve-artifacts`, which means clients only talk to MLflow; they never need direct MinIO credentials. The server proxies artifact uploads and downloads through its own S3 connection.

PostgreSQL was chosen over the default SQLite file because it supports concurrent writers (multiple notebooks, Dagster jobs, and CI runs logging at the same time) and is easy to back up.

MinIO provides an S3-compatible API locally so the same `s3://` URI scheme works here as in cloud deployments. Switching to AWS S3 or GCS later only requires changing two environment variables.

## Default ports

| Service | Port | Variable |
|---|---|---|
| MLflow Tracking UI | 5000 | `MLFLOW_PORT` |
| MinIO S3 API | 9000 | `MINIO_API_PORT` |
| MinIO Console | 9001 | `MINIO_CONSOLE_PORT` |
| PostgreSQL | 5432 | `POSTGRES_PORT` |

## Quick start

```bash
./scripts/start.sh mlflow
```

Python client:

```python
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")

with mlflow.start_run():
    mlflow.log_param("lr", 1e-3)
    mlflow.log_metric("accuracy", 0.93)
    mlflow.log_artifact("confusion_matrix.png")
```

## CRISP-DM role

MLflow is central to the **Modelling** and **Evaluation** phases, and bridges into **Deployment**.

| Phase | What MLflow provides |
|---|---|
| Modelling | Log hyperparameters and architecture choices per run so experiments are reproducible |
| Evaluation | Compare runs side by side in the UI; identify the best configuration by metric |
| Evaluation | Store evaluation artefacts (confusion matrix, ROC curve, feature importance plots) permanently |
| Deployment | Register the selected model in the Model Registry; transition it through Staging to Production |

Without experiment tracking, the Evaluation phase collapses to "the last run I remember." MLflow makes every run a first-class record so you can always go back and explain why a particular model was chosen.
