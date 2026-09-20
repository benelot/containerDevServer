# Dagster

## What it does

[Dagster](https://dagster.io) is a data orchestration platform built around the concept of **software-defined assets**. An asset is a persistent object (a dataset, a trained model, a report) that your code is responsible for producing. Dagster tracks which assets exist, how they depend on each other, and whether they are up to date.

Compared to a pure task scheduler (Airflow, Cron), Dagster's key advantages for data science are:

- **Asset lineage** -- the UI shows which model came from which dataset version
- **Typed asset metadata** -- attach row counts, schema, metrics, and plot previews to any asset
- **Integrated observability** -- every run records logs, timing, and asset materialisation events in one place
- **Incremental materialisation** -- re-run only the assets that are stale or upstream-changed
- **Rich UI** -- visualise the full asset graph before running anything

## Architecture in this stack

```
dagster-webserver  (serves the Dagster UI on port 3000)
dagster-daemon     (runs scheduled jobs, sensors, and backfills)
dagster-postgres   (stores run history, event log, asset catalog)
```

Both the webserver and daemon run from the same Docker image. They share the `DAGSTER_HOME` path (`/opt/dagster`) which contains `dagster.yaml` (PostgreSQL connection) and are pointed at the same `workspace.yaml` (which loads `pipelines/mnist1d_pipeline.py`).

PostgreSQL is used instead of the default SQLite because:
- The webserver and daemon are separate processes; SQLite does not handle concurrent writes safely
- The run history and asset catalog survive image rebuilds

**`extra_hosts: host.docker.internal:host-gateway`** and the MLflow/MinIO environment variables are set for the same reason as in JupyterLab: the pipeline assets log to MLflow and upload artifacts to MinIO, which run on the host network.

## The MNIST 1D pipeline

`pipelines/mnist1d_pipeline.py` defines four software-defined assets:

| Asset | Group | Description |
|---|---|---|
| `raw_dataset` | data | Download MNIST 1D; return train/test arrays |
| `validated_dataset` | quality | Pandera schema check on feature range and label set |
| `data_quality_report` | quality | Evidently drift report + DeepChecks suite; HTML saved and logged to MLflow |
| `trained_model` | training | Conv1D training for 30 epochs; model and metrics logged to MLflow |

Run from the UI or from the CLI:

```bash
docker compose -f services/dagster/docker-compose.yml exec dagster-webserver \
  dagster job execute -j mnist1d_full_pipeline -m pipelines.mnist1d_pipeline
```

## Default ports

| Service | Port | Variable |
|---|---|---|
| Dagster UI | 3000 | `DAGSTER_PORT` |
| PostgreSQL | 5434 | `POSTGRES_PORT` |

## Quick start

```bash
./scripts/start.sh dagster
# Open http://localhost:3000
# Navigate to Assets > Materialize All, or Jobs > mnist1d_full_pipeline > Launch Run
```

## Data quality libraries included

The pipeline (and the `notebooks/data_quality.ipynb` notebook) uses three libraries rather than one:

**Pandera** validates the DataFrame schema at the boundary between data ingestion and modelling. It checks column types, value ranges, and allowed label values. A violation raises an exception immediately, so invalid data never reaches the training step.

**DeepChecks** checks ML-specific properties that Pandera cannot: whether train and test distributions match, whether any features are perfectly correlated with the label (leakage), whether class imbalance is severe. These checks are run as a suite and the HTML report is logged to MLflow.

**Evidently** produces drift and data quality reports in the format expected by the Evidently monitoring UI (`services/evidently/`). It bridges pipeline-time validation and post-deployment monitoring.

The three tools are complementary, not redundant. Great Expectations was considered but excluded: Pandera covers the same DataFrame validation use case with a cleaner API, and the remaining GX features (Data Docs, enterprise governance) are not needed at this scale.

## CRISP-DM role

Dagster orchestrates the **Data Preparation**, **Modelling**, and **Deployment** phases and connects them into a repeatable, observable pipeline.

| Phase | What Dagster provides |
|---|---|
| Data Preparation | `validated_dataset` asset enforces schema before any processing; re-runs automatically if raw data changes |
| Data Preparation | `data_quality_report` asset gates the pipeline on quality -- a bad report fails the run before training starts |
| Modelling | `trained_model` asset is re-materialised whenever the validated dataset or the training code changes |
| Evaluation | Asset metadata (accuracy, loss curves) appears in the Dagster UI alongside MLflow run IDs for cross-referencing |
| Deployment | Scheduled or sensor-triggered re-runs automate retraining when new labeled data arrives from Label Studio |

The Dagster asset graph is the production form of the notebook. A data scientist prototypes the logic in JupyterLab, then promotes it to a Dagster asset so it runs reliably on a schedule.
