from __future__ import annotations

import os
import numpy as np
import bentoml

TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://host.docker.internal:5000")
MODEL_NAME   = os.environ.get("MLFLOW_MODEL_NAME",   "mnist1d-conv1d")
MODEL_STAGE  = os.environ.get("MLFLOW_MODEL_STAGE",  "Production")


@bentoml.service(
    resources={"cpu": "2"},
    traffic={"timeout": 10},
)
class Mnist1DClassifier:
    """
    Serves the MNIST 1D Conv1D classifier from the MLflow Model Registry.

    On startup the service connects to MLflow and downloads the model registered
    under MLFLOW_MODEL_NAME at stage MLFLOW_MODEL_STAGE (default: Production).
    If no Production model exists the service starts in degraded mode: /predict
    returns HTTP 503 and /health reports the reason. Restart the container after
    promoting a model in MLflow to bring the service fully online.
    """

    def __init__(self) -> None:
        import mlflow
        import mlflow.pytorch

        self._model = None
        self._load_error: str | None = None

        mlflow.set_tracking_uri(TRACKING_URI)
        try:
            self._model = mlflow.pytorch.load_model(
                f"models:/{MODEL_NAME}/{MODEL_STAGE}"
            )
            self._model.eval()
            print(f"Loaded {MODEL_NAME}/{MODEL_STAGE} from {TRACKING_URI}")
        except Exception as exc:
            self._load_error = str(exc)
            print(f"WARNING: model not loaded — {self._load_error}")
            print("Service is in degraded mode. Register a Production model in MLflow and restart.")

    @bentoml.api
    def predict(self, sequences: np.ndarray) -> dict:
        """
        Classify one or more MNIST 1D sequences.

        Input:  float32 array of shape (N, 40) — one 40-point sequence per row.
        Output: { "predictions": [int, ...], "probabilities": [[float, ...], ...] }
        """
        if self._model is None:
            raise bentoml.exceptions.ServiceUnavailable(
                f"No model loaded. Register a Production model in MLflow and restart. "
                f"Error: {self._load_error}"
            )
        import torch

        x = torch.tensor(sequences, dtype=torch.float32)
        if x.dim() == 1:
            x = x.unsqueeze(0)     # single sample (40,) -> (1, 40)
        x = x.unsqueeze(1)         # (N, 40) -> (N, 1, 40) for Conv1d

        with torch.no_grad():
            logits = self._model(x)
            probs  = torch.softmax(logits, dim=1)
            preds  = logits.argmax(dim=1)

        return {
            "predictions":   preds.tolist(),
            "probabilities": probs.tolist(),
        }

    @bentoml.api
    def health(self) -> dict:
        """Returns model load status. Used by Docker healthcheck and monitoring probes."""
        if self._model is None:
            return {"status": "degraded", "reason": self._load_error}
        return {"status": "ok", "model": MODEL_NAME, "stage": MODEL_STAGE}
