---
title: "Summary"
weight: 6
---

## What you did

- Started MLflow with a PostgreSQL backend and MinIO artifact store
- Logged a training run with parameters, per-epoch metrics, and a model artifact
- Compared two runs with different hyperparameters
- Registered a model and promoted it to Production

## CRISP-DM phases covered

| Phase | How MLflow contributes |
|---|---|
| Modelling | Every training run is recorded — parameters, metrics, model file |
| Evaluation | Compare runs side by side; pick the best candidate for production |
| Deployment | Model Registry stores versioned models; stage transitions drive the deploy process |

## Key commands

```python
# Log a run
mlflow.set_experiment("my-experiment")
with mlflow.start_run():
    mlflow.log_params({...})
    mlflow.log_metric("val_acc", acc, step=epoch)
    mlflow.pytorch.log_model(model, "model",
                             registered_model_name="my-model")

# Promote to Production
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage("my-model", version=1, stage="Production")

# Load from registry
model = mlflow.pytorch.load_model("models:/my-model/Production")
```

## What is next

[Lab 2 — JupyterLab]({{< relref "../02-jupyterlab" >}}) uses the same MLflow server to log an interactive exploration session, then runs the full CRISP-DM example notebook end to end.
