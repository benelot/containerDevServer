---
title: "Setup"
weight: 2
---

## Start the service

```bash
./scripts/start.sh mlflow
```

On first run this copies `.env.example` to `.env` and starts four containers: the MLflow server, PostgreSQL, MinIO, and a MinIO setup container that creates the artifact bucket.

After about 30 seconds all four containers will be healthy. Verify:

```bash
curl {{< svcurl "mlflow_port" >}}/health
# → {"status":"ok"}
```

## Open the UI

Go to **{{< svcurl "mlflow_port" >}}** in your browser. You will see an empty MLflow home page with no experiments yet.

The three icons on the left sidebar are:
- **Experiments** — list of all experiments and their runs
- **Models** — the Model Registry
- **Artifacts** — direct MinIO browse (rarely used; artifacts load from run pages)

## Connect from Python

The JupyterLab and Dagster containers already have `MLFLOW_TRACKING_URI` set in their environment, so they connect automatically. If you are working outside those containers:

```python
import mlflow
mlflow.set_tracking_uri("{{< svcurl "mlflow_port" >}}")
print(mlflow.get_tracking_uri())
# http://localhost:{{< port "mlflow_port" >}}
```

{{% notice style="info" %}}
The MLflow server uses `--serve-artifacts`, which means artifact uploads go through `http://localhost:{{< port "mlflow_port" >}}/api/2.0/mlflow-artifacts/`. You do not need to configure MinIO credentials on the client side.
{{% /notice %}}

## Stop the service

```bash
./scripts/start.sh mlflow --stop
```
