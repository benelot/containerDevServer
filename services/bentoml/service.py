from __future__ import annotations

import os
import numpy as np
import bentoml
from bentoml.io import NumpyNdarray, JSON

TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://host.docker.internal:5000")
MODEL_NAME   = os.environ.get("MLFLOW_MODEL_NAME", "mnist1d-conv1d")
MODEL_STAGE  = os.environ.get("MLFLOW_MODEL_STAGE", "Production")

# --------------------------------------------------------------------------- #
# Load model from MLflow registry at startup
# --------------------------------------------------------------------------- #
import mlflow
import mlflow.pytorch
import torch

mlflow.set_tracking_uri(TRACKING_URI)

_model = None
_load_error = None

try:
    _model = mlflow.pytorch.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")
    _model.eval()
    print(f"Loaded {MODEL_NAME}/{MODEL_STAGE} from {TRACKING_URI}")
except Exception as exc:
    _load_error = str(exc)
    print(f"WARNING: could not load model -- {_load_error}")
    print("Service will return 503 until a Production model is registered in MLflow.")

# --------------------------------------------------------------------------- #
# BentoML runner
# --------------------------------------------------------------------------- #
mnist1d_runner = bentoml.Runner(
    bentoml.picklable_model.get("mnist1d") if _model is None else None,
    name="mnist1d_runner",
)

svc = bentoml.Service("mnist1d_classifier", runners=[])


@svc.api(input=NumpyNdarray(dtype="float32", shape=(-1, 40)), output=JSON())
def predict(sequences: np.ndarray) -> dict:
    """
    Input:  float32 array of shape (N, 40)  -- one row per sample
    Output: {"predictions": [int, ...], "probabilities": [[float, ...], ...]}
    """
    if _model is None:
        raise bentoml.exceptions.ServiceUnavailable(
            f"No model loaded. Register a Production model in MLflow first. "
            f"Error was: {_load_error}"
        )

    x = torch.tensor(sequences, dtype=torch.float32)
    if x.dim() == 1:
        x = x.unsqueeze(0)         # (1, 40)
    x = x.unsqueeze(1)             # (N, 1, 40)

    with torch.no_grad():
        logits = _model(x)
        probs  = torch.softmax(logits, dim=1)
        preds  = logits.argmax(dim=1)

    return {
        "predictions":   preds.tolist(),
        "probabilities": probs.tolist(),
    }


@svc.api(input=JSON(), output=JSON())
def health(_: dict) -> dict:
    if _model is None:
        return {"status": "degraded", "reason": _load_error}
    return {"status": "ok", "model": MODEL_NAME, "stage": MODEL_STAGE}
