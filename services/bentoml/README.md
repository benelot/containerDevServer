# BentoML

## What it does

[BentoML](https://bentoml.com) is a model serving framework that turns a trained model into a production-ready REST API. It handles:

- **HTTP endpoints** with automatic OpenAPI/Swagger documentation
- **Input/output validation** with typed schemas
- **Batching** -- multiple requests are grouped into a single model forward pass
- **Health checks** -- a `/health` endpoint reports whether the model loaded successfully
- **Containerisation** -- `bentoml build` + `bentoml containerize` packages the service into a self-contained Docker image for any deployment target

## Architecture in this stack

On startup the container connects to the MLflow Tracking server, downloads the model registered under `MLFLOW_MODEL_NAME` at stage `MLFLOW_MODEL_STAGE` (default: `Production`), and begins serving. Model weights are fetched from MinIO via the MLflow artifact proxy, so the serving container needs the same MLflow and MinIO environment variables as the training containers.

If no Production model exists yet the service starts in **degraded mode**: it returns HTTP 503 on `/predict` and reports the reason in `/health`. This makes the startup order safe -- you can bring BentoML up alongside the rest of the stack and it self-heals once a model is promoted.

```
client
  |
  v
bentoml container (port 3001)
  |
  +-- GET /health   -->  {"status": "ok", "model": "mnist1d-conv1d", "stage": "Production"}
  +-- POST /predict -->  {"predictions": [3], "probabilities": [[0.01, ..., 0.92, ...]]}
  |
  +-- MLflow registry  (pulls model URI on startup)
  +-- MinIO            (downloads model weights via MLflow artifact proxy)
```

Port 3001 is used to avoid conflict with the Dagster UI on 3000.

## Default ports

| Service | Port | Variable |
|---|---|---|
| BentoML REST API | 3001 | `BENTOML_PORT` |

## Prerequisites

The MLflow stack must be running and a model must be registered and promoted to Production before predictions work:

```python
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")

# After training:
result = mlflow.register_model("runs:/<run_id>/model", "mnist1d-conv1d")

from mlflow.tracking import MlflowClient
client = MlflowClient()
client.transition_model_version_stage(
    name="mnist1d-conv1d",
    version=result.version,
    stage="Production",
)
```

The CRISP-DM notebook (`notebooks/mnist1d_crisp_dm.ipynb`) does this automatically in the Deployment section.

## Quick start

```bash
# Start MLflow first and register a Production model
./scripts/start.sh mlflow

# Then start BentoML
./scripts/start.sh bentoml

# Check health
curl http://localhost:3001/health

# Run a prediction (40-value MNIST 1D sequence)
curl -X POST http://localhost:3001/predict \
  -H "Content-Type: application/json" \
  -d '[[0.1, -0.2, 0.3, ..., 0.0]]'

# Swagger UI (interactive API docs)
open http://localhost:3001
```

## Swapping the model

Change `MLFLOW_MODEL_NAME` and `MLFLOW_MODEL_STAGE` in `.env` and restart the container. No code change is needed -- the service reads those values at startup.

## CRISP-DM role

BentoML is the **Deployment** phase made concrete. It is the point where the model transitions from a registry entry to a callable service.

| Phase | What BentoML provides |
|---|---|
| Deployment | Serve the Production model as a REST API that any downstream system can call |
| Deployment | Swagger UI lets non-engineers test the model directly without writing code |
| Evaluation | The `/health` endpoint makes it observable -- monitoring tools can confirm the right model version is live |
| Deployment | Model swaps are zero-downtime: promote a new version in MLflow and restart the container |

Evidently monitors the requests flowing through this endpoint. When it detects drift in the incoming sequences, it triggers the re-labeling and retraining loop that produces a new Production model -- which BentoML then serves automatically on the next restart.
