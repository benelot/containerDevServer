# BentoML

Model serving layer for the CRISP-DM Deployment phase.

## CRISP-DM role

| Phase | Contribution |
|---|---|
| Deployment | Expose the registered MLflow model as a typed REST API with automatic documentation |

BentoML bridges the Model Registry and external consumers. A model trained in a notebook or by the Dagster pipeline is registered in MLflow, promoted to Production, and immediately available via the BentoML REST endpoint — with no code changes required.

## How it works

On startup the service connects to MLflow and loads the model registered under `MLFLOW_MODEL_NAME` at stage `MLFLOW_MODEL_STAGE`. If no model at that stage exists yet, the service starts in **degraded mode**: `/predict` returns HTTP 503 with a clear explanation, and `/health` reports the reason. This makes startup order safe — BentoML can launch alongside the rest of the stack and become fully operational once a model is promoted.

```
MLflow Model Registry
        │  load on startup
        ▼
  BentoML service  ──► /predict   (POST, numpy array → predictions + probabilities)
                   ──► /health    (GET, model load status)
                   ──► /docs      (Swagger UI)
```

## Quickstart

```bash
./scripts/start.sh bentoml
# http://localhost:3001        — Swagger UI
# http://localhost:3001/health — model load status
```

Classify a batch of MNIST 1D sequences:

```bash
curl -X POST http://localhost:3001/predict \
  -H "Content-Type: application/json" \
  -d '[[0.1, -0.2, 0.3, 0.5, -0.1, 0.4, 0.2, -0.3, 0.6, 0.1,
        0.0, -0.1, 0.2, 0.4, -0.2, 0.3, 0.1, 0.5, -0.4, 0.2,
        0.3, -0.1, 0.4, 0.2, -0.3, 0.5, 0.1, 0.0, 0.2, -0.1,
        0.4, 0.3, -0.2, 0.1, 0.5, -0.3, 0.2, 0.4, -0.1, 0.3]]'
# {"predictions": [3], "probabilities": [[0.01, 0.02, 0.03, 0.92, ...]]}
```

## API endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/predict` | POST | Classify one or more sequences. Input: float32 array of shape `(N, 40)`. Output: predicted class indices and class probabilities. |
| `/health` | GET | Returns model load status. Use for Docker healthchecks and uptime probes. |
| `/docs` | GET | Interactive Swagger UI. |

## Serving a different model

Change `MLFLOW_MODEL_NAME` or `MLFLOW_MODEL_STAGE` in `.env` and restart the container:

```bash
# services/bentoml/.env
MLFLOW_MODEL_NAME=my-other-model
MLFLOW_MODEL_STAGE=Staging
```

No code changes required.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `BENTOML_PORT` | `3001` | BentoML serving port |
| `MLFLOW_TRACKING_URI` | `http://host.docker.internal:5000` | MLflow server visible from inside the container |
| `MLFLOW_MODEL_NAME` | `mnist1d-conv1d` | Registered model name to load |
| `MLFLOW_MODEL_STAGE` | `Production` | Model Registry stage to load |
