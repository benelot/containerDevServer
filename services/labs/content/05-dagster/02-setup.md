---
title: "Setup"
weight: 2
---

## Start the services

```bash
./scripts/start.sh dagster
./scripts/start.sh mlflow
```

Dagster opens at **{{< svcurl "dagster_port" >}}**.

Verify the webserver is up:

```bash
curl -s {{< svcurl "dagster_port" >}}/dagster/version
# → {"version":"..."}
```

## Explore the UI

Open the Dagster UI and navigate to **Asset Catalog** in the left sidebar. You should see four assets grouped under three groups:

- **data**: `raw_dataset`, `validated_dataset`
- **quality**: `data_quality_report`
- **training**: `trained_model`

Click any asset to see its description, upstream dependencies, and materialisation history.

Navigate to **Jobs** and click `mnist1d_full_pipeline`. The job graph shows all four assets connected by dependency arrows. This is your pipeline.

## Verify the pipeline file

The pipeline lives at `services/dagster/pipelines/mnist1d_pipeline.py`. Dagster loads it via the Compose environment variable `DAGSTER_WORKING_DIRECTORY`. You can read it at any time to trace exactly what each asset does:

```bash
cat services/dagster/pipelines/mnist1d_pipeline.py
```

## Configure MLflow tracking URI

The pipeline logs to MLflow automatically. The MLflow tracking URI is set in `services/dagster/.env` (or `.env.example`):

```bash
grep MLFLOW services/dagster/.env.example
# MLFLOW_TRACKING_URI=http://host.docker.internal:5000
```

The `host.docker.internal` hostname lets the Dagster container reach the MLflow server running on the host machine. If MLflow is not running when the pipeline executes, the training asset will log a warning and continue — the model is still trained, but the run will not appear in MLflow.

{{% expand title="Start here if you skipped earlier labs" %}}
You only need Dagster and MLflow. No prior dataset, DVC, or Label Studio state is required — the `raw_dataset` asset downloads the data itself.
```bash
./scripts/start.sh dagster
./scripts/start.sh mlflow
```
{{% /expand %}}
