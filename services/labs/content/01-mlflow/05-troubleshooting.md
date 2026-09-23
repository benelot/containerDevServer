---
title: "Troubleshooting"
weight: 5
---

## Common issues

### "Connection refused" when calling `mlflow.set_tracking_uri`

The MLflow server takes about 20–30 seconds to start after `docker compose up`. Wait until `curl {{< svcurl "mlflow_port" >}}/health` returns `{"status":"ok"}` before connecting from Python.

### Artifact upload fails with "403 Forbidden"

This usually means the MinIO bucket was not created. Check the setup container log:

```bash
docker compose -f services/mlflow/docker-compose.yml logs mlflow-setup
```

If the bucket creation failed, restart the stack:

```bash
./scripts/start.sh mlflow --stop
./scripts/start.sh mlflow
```

### "MLFLOW_S3_ENDPOINT_URL" errors from inside JupyterLab or Dagster

The `--serve-artifacts` flag routes all artifact traffic through the MLflow HTTP API, so you should never need to set `MLFLOW_S3_ENDPOINT_URL` on the client. If you see S3 errors, check that you are connecting to the MLflow server URL (port {{< port "mlflow_port" >}}), not directly to MinIO (port {{< port "mlflow_minio_port" >}}).

### Two runs with the same name appear

MLflow does not enforce unique run names. The run name is a display label; the run ID is what uniquely identifies a run. Use `run.info.run_id` when you need a stable reference.

### The Model Registry is empty after training

`log_model` with `registered_model_name` registers the model automatically. If the registry is empty, check that:
1. The training run completed with status `FINISHED` (not `FAILED`)
2. You passed `registered_model_name` to `log_model`
3. You are looking at the **Models** tab, not the **Experiments** tab

### PostgreSQL "too many connections"

The default connection pool is sufficient for 2–3 concurrent processes. If you are running more than that (several notebooks plus Dagster), increase `POSTGRES_MAX_CONNECTIONS` in `services/mlflow/.env` and restart.
