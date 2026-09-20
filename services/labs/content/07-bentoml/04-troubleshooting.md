---
title: "Troubleshooting"
weight: 4
---

## Common issues

### `/health` returns `{"status":"degraded"}`

No Production model is loaded. Check:

1. Is MLflow running? `curl {{< svcurl "mlflow_port" >}}/health`
2. Is a model registered at stage `Production`? Open **{{< svcurl "mlflow_port" >}}** → **Models → mnist1d-conv1d**.
3. If a model exists but BentoML still reports degraded, the container started before the model was promoted. Restart:

```bash
docker compose -f services/bentoml/docker-compose.yml restart bentoml
```

### `/predict` returns HTTP 422 "Unprocessable Entity"

The request body does not match the expected schema. BentoML expects the key `sequences` with a 2-D array:

```json
{"sequences": [[0.1, 0.2, ...]]}   ← correct (list of lists)
{"sequences":  [0.1, 0.2, ...]}    ← wrong (1-D — wrap in an outer list)
```

Each inner list must have exactly 40 elements — the feature dimension the Conv1D was trained on.

### `/predict` returns HTTP 503 "Service Unavailable"

The model is in degraded mode (same as the health issue above). See the fix above.

### Container exits immediately at startup

Check logs:

```bash
docker compose -f services/bentoml/docker-compose.yml logs bentoml
```

A common cause is a missing `service.py` or an import error. The entrypoint runs `bentoml serve service:Mnist1DClassifier` — if `service.py` is not found or has a syntax error the container exits. Rebuild:

```bash
docker compose -f services/bentoml/docker-compose.yml build --no-cache
docker compose -f services/bentoml/docker-compose.yml up -d
```

### Predictions are all the same class

The model may not have trained to convergence. Check the val_acc metric in the MLflow run — if it never exceeded 50%, the model is not useful. Re-run the Dagster pipeline with more epochs or a lower learning rate, promote the new version, and restart BentoML.

### BentoML cannot reach MLflow (`host.docker.internal` not resolving)

On Linux, `host.docker.internal` requires the container to have `extra_hosts: ["host.docker.internal:host-gateway"]`. Verify this is in `services/bentoml/docker-compose.yml`. If it is missing, add it or set `MLFLOW_TRACKING_URI` to the host machine's LAN IP address in `services/bentoml/.env`.
