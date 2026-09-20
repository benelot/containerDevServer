---
title: "Setup"
weight: 2
---

## Prerequisites

BentoML loads its model from MLflow at startup. MLflow must be running and a model must be at stage **Production** before you start BentoML.

If you have not yet promoted a model:

1. Start MLflow: `./scripts/start.sh mlflow`
2. Trigger the Dagster pipeline (Lab 5) to train and register a model, **or** register one manually (see below).
3. In the MLflow UI at **{{< svcurl "mlflow_port" >}}** → **Models → mnist1d-conv1d** → latest version → **Stage → Production**.

### Register a model without Dagster

```python
import mlflow, mlflow.pytorch, torch, torch.nn as nn

TRACKING_URI = "{{< svcurl "mlflow_port" >}}"
mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment("mnist1d-bentoml-quickstart")

class TinyConv(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(1, 16, 5, padding=2), nn.ReLU(),
            nn.AdaptiveAvgPool1d(1), nn.Flatten(),
            nn.Linear(16, 10)
        )
    def forward(self, x): return self.net(x)

model = TinyConv().eval()

with mlflow.start_run(run_name="quickstart"):
    mlflow.pytorch.log_model(
        model, "model", registered_model_name="mnist1d-conv1d"
    )

print("Registered. Now promote to Production in the MLflow UI.")
```

## Start BentoML

```bash
./scripts/start.sh bentoml
```

BentoML opens at **{{< svcurl "bentoml_port" >}}**.

Verify the model loaded:

```bash
curl {{< svcurl "bentoml_port" >}}/health
# {"status":"ok","model":"mnist1d-conv1d","stage":"Production"}
```

If you see `{"status":"degraded",...}`, check that a Production model exists in MLflow and restart:

```bash
docker compose -f services/bentoml/docker-compose.yml restart bentoml
```

{{% expand title="Start here if you skipped earlier labs" %}}
Use the quickstart script above to register a minimal model, promote it to Production, then start BentoML.
```bash
./scripts/start.sh mlflow
./scripts/start.sh bentoml
```
{{% /expand %}}
