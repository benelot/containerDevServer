---
title: "Track your first experiment"
weight: 3
---

## The scenario

You are going to train a Conv1D classifier on MNIST 1D and log everything to MLflow. The code below uses the MNIST 1D generator to produce the dataset, trains for 10 epochs, and records parameters, per-epoch validation accuracy, and the model artifact.

Run this in a Python environment where `mlflow`, `torch`, and `mnist1d` are installed. If you are using JupyterLab, start it first:

```bash
./scripts/start.sh jupyterlab
# Open http://localhost:{{< port "jupyter_port" >}}
```

{{% expand title="Start here if you skipped earlier labs" %}}
Install the packages and generate data:
```bash
pip install mlflow torch mnist1d
```
```python
from mnist1d.data import make_dataset, get_dataset_args
data = make_dataset(get_dataset_args())
```
{{% /expand %}}

## Training code

Open a new notebook and paste this:

```python
import mlflow, mlflow.pytorch, torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from mnist1d.data import make_dataset, get_dataset_args

# ── Data ──────────────────────────────────────────────────────────────────────
data  = make_dataset(get_dataset_args())
X_tr  = torch.tensor(data['x'],      dtype=torch.float32).unsqueeze(1)  # (N,1,40)
y_tr  = torch.tensor(data['y'],      dtype=torch.long)
X_te  = torch.tensor(data['x_test'], dtype=torch.float32).unsqueeze(1)
y_te  = torch.tensor(data['y_test'], dtype=torch.long)
loader = DataLoader(TensorDataset(X_tr, y_tr), batch_size=128, shuffle=True)

# ── Model ─────────────────────────────────────────────────────────────────────
class Conv1DNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(1, 32, 5, padding=2), nn.ReLU(), nn.MaxPool1d(2),
            nn.Conv1d(32, 64, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool1d(1),
            nn.Flatten(), nn.Linear(64, 10),
        )
    def forward(self, x): return self.net(x)

# ── Training with MLflow ──────────────────────────────────────────────────────
mlflow.set_tracking_uri("{{< svcurl "mlflow_port" >}}")
mlflow.set_experiment("mnist1d")

with mlflow.start_run(run_name="conv1d-first-run") as run:
    mlflow.log_params({"epochs": 10, "lr": 1e-3, "batch_size": 128})

    model = Conv1DNet()
    opt   = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(1, 11):
        model.train()
        for xb, yb in loader:
            opt.zero_grad(); loss_fn(model(xb), yb).backward(); opt.step()

        model.eval()
        with torch.no_grad():
            acc = (model(X_te).argmax(1) == y_te).float().mean().item()
        mlflow.log_metric("val_acc", acc, step=epoch)
        print(f"Epoch {epoch:2d}  val_acc={acc:.3%}")

    mlflow.pytorch.log_model(model, "model",
                             registered_model_name="mnist1d-conv1d")
    print(f"\nRun ID: {run.info.run_id}")
```

## Inspect the run

1. Open **{{< svcurl "mlflow_port" >}}**.
2. Click the **mnist1d** experiment.
3. Click the run named **conv1d-first-run**.

You will see:

| Section | What is there |
|---|---|
| **Overview** | Run ID, duration, status |
| **Parameters** | `epochs=10`, `lr=0.001`, `batch_size=128` |
| **Metrics** | `val_acc` chart with 10 data points |
| **Artifacts** | `model/` directory containing `MLmodel`, `model.pth`, `requirements.txt` |

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Confirm the run appears in the MLflow UI with status **FINISHED**
- [ ] Find the final `val_acc` value and record it
- [ ] Run the training cell a second time with `lr=5e-4` — observe a second run appears in the experiment list
- [ ] Use the **Compare** button to view both runs side by side
{{% /notice %}}

## What just happened

When you called `mlflow.log_metric("val_acc", acc, step=epoch)`, MLflow stored that value in PostgreSQL. When `mlflow.pytorch.log_model(...)` ran, it serialised the PyTorch model and uploaded it to MinIO via the server's artifact proxy. The `registered_model_name` argument registered the model in the Model Registry at the same time.
