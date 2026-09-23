# Dagster

Pipeline orchestrator for the CRISP-DM Data Preparation, Modelling, and Evaluation phases.

## CRISP-DM role

| Phase | Contribution |
|---|---|
| Data Preparation | Validate schema at ingestion time; reject bad data before it reaches training |
| Modelling | Train the model as a reproducible, logged asset |
| Evaluation | Run data quality suites automatically on every pipeline execution |
| Deployment | Schedule retraining when new labeled data arrives from Label Studio |

## Asset graph

The `mnist1d_full_pipeline` job materialises four assets in sequence:

```
raw_dataset
    │
    ▼
validated_dataset  ──►  data_quality_report
    │
    ▼
trained_model
```

| Asset | What it does |
|---|---|
| `raw_dataset` | Downloads the MNIST 1D dataset (cached locally after first run) |
| `validated_dataset` | Validates feature ranges and label domain with Pandera |
| `data_quality_report` | Runs Evidently drift + quality reports and DeepChecks integrity suites; logs all HTML artifacts and pass/fail counts to MLflow |
| `trained_model` | Trains a Conv1D network; logs all metrics and registers the model in MLflow as `mnist1d-conv1d` |

## Data quality libraries

**Pandera** validates DataFrame schema at the ingestion boundary. It checks column types, value ranges (features must be in `[-8, 8]`), and label domain (integers 0–9). A schema violation raises an exception and halts the pipeline before any bad data reaches training.

**DeepChecks** runs ML-specific suites on the training and test splits: class balance, duplicate samples, feature leakage, and train/test distribution. Results are saved as interactive HTML reports and logged to MLflow.

**Evidently** generates drift and data quality reports that flow into the monitoring UI. The same reports a data scientist reviews manually can be watched automatically for regressions in production.

## Quickstart

```bash
./scripts/start.sh dagster
# http://localhost:3000
```

Run the full pipeline: **Assets → Materialize All**, or **Jobs → mnist1d_full_pipeline → Launch Run**.

## Services

| Container | Port | Purpose |
|---|---|---|
| `dagster-webserver` | 3000 | Dagster UI |
| `dagster-daemon` | — | Scheduler and sensor daemon |
| `dagster-db` | 5434 | PostgreSQL — run history and asset metadata |

Webserver and daemon share the same Docker image and the same PostgreSQL database. The daemon handles scheduled runs and sensors; the webserver handles the UI and manual launches.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DAGSTER_PORT` | `3000` | Webserver port |
| `POSTGRES_PORT` | `5434` | PostgreSQL port (offset from MLflow 5432 and Label Studio 5433) |
| `MLFLOW_TRACKING_URI` | `http://host.docker.internal:5000` | MLflow server visible from inside the container |
| `MLFLOW_S3_ENDPOINT_URL` | `http://host.docker.internal:9000` | MinIO endpoint for artifact uploads |
