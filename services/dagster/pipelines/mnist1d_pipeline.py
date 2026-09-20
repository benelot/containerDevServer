"""
Dagster asset pipeline — MNIST 1D CRISP-DM cycle.

Asset graph:
  raw_dataset  ──►  validated_dataset  ──►  trained_model
                         │
                         └──►  data_quality_report
"""
import os
import pickle
import urllib.request

import dagster as dg
import numpy as np
import pandas as pd
import pandera as pa
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import mlflow
import mlflow.pytorch
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset


# ── Pandera schema ─────────────────────────────────────────────────────────────

def _build_schema(n_features: int = 40) -> pa.DataFrameSchema:
    cols = {f"t{i}": pa.Column(float, pa.Check.between(-8.0, 8.0)) for i in range(n_features)}
    cols["label"] = pa.Column(int, pa.Check.isin(list(range(10))))
    return pa.DataFrameSchema(cols, coerce=True)


# ── Assets ─────────────────────────────────────────────────────────────────────

@dg.asset(group_name="data", description="Download MNIST 1D from GitHub or local cache")
def raw_dataset(context: dg.AssetExecutionContext) -> dict:
    cache = "/tmp/mnist1d_data.pkl"
    if not os.path.exists(cache):
        url = "https://github.com/greydanus/mnist1d/raw/master/mnist1d_data.pkl"
        context.log.info(f"Downloading MNIST 1D → {cache}")
        urllib.request.urlretrieve(url, cache)
    with open(cache, "rb") as f:
        data = pickle.load(f)
    out = {
        "X_train": np.array(data["x"],      dtype=np.float32),
        "y_train": np.array(data["y"],      dtype=np.int64),
        "X_test":  np.array(data["x_test"], dtype=np.float32),
        "y_test":  np.array(data["y_test"], dtype=np.int64),
    }
    context.log.info(f"Train: {out['X_train'].shape}  Test: {out['X_test'].shape}")
    return out


@dg.asset(group_name="data", description="Validate feature range and label domain with Pandera")
def validated_dataset(context: dg.AssetExecutionContext, raw_dataset: dict) -> dict:
    X, y = raw_dataset["X_train"], raw_dataset["y_train"]
    df = pd.DataFrame(X, columns=[f"t{i}" for i in range(X.shape[1])])
    df["label"] = y
    schema = _build_schema(X.shape[1])
    schema.validate(df)
    context.log.info(f"Pandera validation passed — {len(df):,} rows × {X.shape[1]} features")
    return raw_dataset


@dg.asset(
    group_name="quality",
    description="Evidently data-quality + drift report (train reference vs test current)",
)
def data_quality_report(context: dg.AssetExecutionContext, validated_dataset: dict) -> str:
    cols = [f"t{i}" for i in range(validated_dataset["X_train"].shape[1])]
    ref = pd.DataFrame(validated_dataset["X_train"], columns=cols)
    ref["label"] = validated_dataset["y_train"]
    cur = pd.DataFrame(validated_dataset["X_test"], columns=cols)
    cur["label"] = validated_dataset["y_test"]

    report = Report(metrics=[DataQualityPreset(), DataDriftPreset()])
    report.run(reference_data=ref, current_data=cur)

    out_path = "/tmp/evidently_report.html"
    report.save_html(out_path)
    context.log.info(f"Evidently report → {out_path}")

    # Log to MLflow if reachable
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    try:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("mnist1d-dagster")
        with mlflow.start_run(run_name="evidently-report"):
            mlflow.log_artifact(out_path, "evidently")
        context.log.info("Evidently report logged to MLflow")
    except Exception as e:
        context.log.warning(f"Could not log to MLflow: {e}")

    return out_path


@dg.asset(
    group_name="training",
    description="Train Conv1D on validated data and register model in MLflow",
)
def trained_model(context: dg.AssetExecutionContext, validated_dataset: dict) -> str:
    X_train = validated_dataset["X_train"]
    y_train = validated_dataset["y_train"]
    X_test  = validated_dataset["X_test"]
    y_test  = validated_dataset["y_test"]

    device = "cpu"
    mean, std = X_train.mean(), X_train.std()
    X_tr = torch.from_numpy(((X_train - mean) / std)[:, None, :])
    X_te = torch.from_numpy(((X_test  - mean) / std)[:, None, :])
    y_tr = torch.from_numpy(y_train)
    y_te = torch.from_numpy(y_test)

    train_ld = DataLoader(TensorDataset(X_tr, y_tr), batch_size=128, shuffle=True)
    test_ld  = DataLoader(TensorDataset(X_te, y_te), batch_size=128)

    class Conv1DNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv1d(1,   32, 5, padding=2), nn.BatchNorm1d(32),  nn.ReLU(), nn.MaxPool1d(2),
                nn.Conv1d(32,  64, 3, padding=1), nn.BatchNorm1d(64),  nn.ReLU(), nn.MaxPool1d(2),
                nn.Conv1d(64, 128, 3, padding=1), nn.BatchNorm1d(128), nn.ReLU(),
                nn.AdaptiveAvgPool1d(1), nn.Flatten(),
                nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.3), nn.Linear(64, 10),
            )
        def forward(self, x): return self.net(x)

    model = Conv1DNet()
    optimiser = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("mnist1d-dagster")

    with mlflow.start_run(run_name="dagster-conv1d") as run:
        mlflow.log_params({"epochs": 30, "batch_size": 128, "lr": 1e-3, "source": "dagster"})

        for epoch in range(1, 31):
            model.train()
            for xb, yb in train_ld:
                optimiser.zero_grad()
                criterion(model(xb), yb).backward()
                optimiser.step()

            if epoch % 5 == 0 or epoch == 1:
                model.eval()
                with torch.no_grad():
                    preds = torch.cat([model(xb).argmax(1) for xb, _ in test_ld])
                acc = (preds == y_te).float().mean().item()
                mlflow.log_metric("val_acc", acc, step=epoch)
                context.log.info(f"Epoch {epoch:2d}  val_acc={acc:.3%}")

        model_info = mlflow.pytorch.log_model(
            model, "model", registered_model_name="mnist1d-dagster"
        )
        run_id = run.info.run_id

    context.log.info(f"Model registered — run_id={run_id}")
    return run_id


# ── Job and definitions ────────────────────────────────────────────────────────

mnist1d_job = dg.define_asset_job(
    "mnist1d_full_pipeline",
    selection=dg.AssetSelection.all(),
    description="Download → validate → quality-report → train → register",
)

defs = dg.Definitions(
    assets=[raw_dataset, validated_dataset, data_quality_report, trained_model],
    jobs=[mnist1d_job],
)
