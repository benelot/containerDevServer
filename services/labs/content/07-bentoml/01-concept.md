---
title: "Concept"
weight: 1
---

## What BentoML does

BentoML is a framework for serving ML models as HTTP services. In this stack it does one specific job: load the `mnist1d-conv1d` model at stage `Production` from the MLflow registry and expose it as a `/predict` REST endpoint.

### Key terms

| Term | Meaning |
|---|---|
| **Service class** | A Python class decorated with `@bentoml.service` — one class = one service |
| **API method** | A method decorated with `@bentoml.api` — one method = one endpoint |
| **Degraded mode** | The service starts even if the model fails to load; `/predict` returns HTTP 503 |
| **`models:/name/stage`** | MLflow URI format to load a model by registry name and lifecycle stage |

### The service class

```python
@bentoml.service(resources={"cpu": "2"}, traffic={"timeout": 10})
class Mnist1DClassifier:
    def __init__(self):
        self._model = mlflow.pytorch.load_model("models:/mnist1d-conv1d/Production")
        self._model.eval()

    @bentoml.api
    def predict(self, sequences: np.ndarray) -> dict:
        # sequences: shape (N, 40)
        # returns {"predictions": [...], "probabilities": [[...]]}
        ...

    @bentoml.api
    def health(self) -> dict:
        # returns {"status": "ok"} or {"status": "degraded", "reason": "..."}
        ...
```

The `__init__` method runs once at startup. If the MLflow registry has no Production model, the service logs a warning and starts in degraded mode — every `/predict` call returns HTTP 503 until you restart the container after promoting a model.

### Why degraded mode matters

In a real system, services must start even when dependencies are unavailable. BentoML's degraded mode means the container passes its health check immediately, and the model becomes available as soon as you promote a version in MLflow and restart — no redeployment required.

### Input and output format

**Input:** A JSON body with a `sequences` key containing a 2-D float array:
```json
{"sequences": [[0.1, -0.3, 0.5, ...]]}
```

**Output:** Predictions and per-class probabilities:
```json
{
  "predictions": [3],
  "probabilities": [[0.01, 0.02, 0.05, 0.82, ...]]
}
```

`predictions[i]` is the digit class (0–9) with the highest probability for input row `i`.
