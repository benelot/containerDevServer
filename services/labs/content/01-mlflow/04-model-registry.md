---
title: "Model Registry"
weight: 4
---

## What the registry is for

The Experiment view answers "which run was best?" The Model Registry answers "which model is in production right now?"

Every model registered during a run appears in the registry under a name. Each new registration of the same name creates a new version. Versions move through stages — Staging, Production — as they are reviewed and deployed.

BentoML reads the `Production` version of `mnist1d-conv1d` on startup. Changing what is in Production is the entire deployment process.

## Promote a model to Production

### Via the UI

1. Open **{{< svcurl "mlflow_port" >}}** → **Models** → `mnist1d-conv1d`.
2. You will see `Version 1` (and `Version 2` if you ran the training twice).
3. Click `Version 1`.
4. Click the **Stage** dropdown → **Transition to Production** → confirm.

### Via the Python client

```python
import mlflow
client = mlflow.tracking.MlflowClient(
    tracking_uri="{{< svcurl "mlflow_port" >}}"
)

# Find the version with the best val_acc
versions = client.search_model_versions("name='mnist1d-conv1d'")
best = max(versions, key=lambda v: float(
    client.get_metric_history(v.run_id, "val_acc")[-1].value
))

client.transition_model_version_stage(
    name="mnist1d-conv1d",
    version=best.version,
    stage="Production",
)
print(f"Promoted version {best.version} to Production")
```

## Load a model from the registry

Once a version is in Production, any Python process can load it by stage name:

```python
import mlflow.pytorch
mlflow.set_tracking_uri("{{< svcurl "mlflow_port" >}}")

model = mlflow.pytorch.load_model("models:/mnist1d-conv1d/Production")
model.eval()
print("Loaded:", type(model))
```

This is exactly what BentoML does on startup. The URI `models:/mnist1d-conv1d/Production` always resolves to whatever version is currently staged as Production, so you can deploy a new model without touching the serving code.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Promote your best run's model to Production via the UI
- [ ] Verify the stage shows **Production** on the model version page
- [ ] Load the Production model in a notebook using the `models:/` URI
- [ ] Run inference on one MNIST 1D sample and print the predicted class
{{% /notice %}}

## Archiving old versions

When a model is replaced, set the old version to Archived so it does not clutter the registry but is still kept for audit:

```python
client.transition_model_version_stage(
    name="mnist1d-conv1d",
    version=1,
    stage="Archived",
)
```

{{% notice style="tip" %}}
Archived models are still accessible and loadable. Archiving is a label, not a deletion. Use the MLflow UI or `client.delete_model_version()` to permanently remove a version.
{{% /notice %}}
