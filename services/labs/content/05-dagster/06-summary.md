---
title: "Summary"
weight: 6
---

## What you did

- Explored the Dagster asset graph and understood the four-asset dependency structure
- Traced each asset to its purpose: download, validate (Pandera), quality-report (Evidently + DeepChecks), train (Conv1D + MLflow)
- Triggered a full pipeline run and confirmed all assets materialised successfully
- Inspected the Evidently drift report and DeepChecks suite results in MLflow
- Promoted the trained model to Production in the MLflow registry

## CRISP-DM phases covered

| Phase | Asset |
|---|---|
| Data Understanding | `data_quality_report` — Evidently + DeepChecks surface distribution problems before training |
| Data Preparation | `validated_dataset` — Pandera schema enforces structural correctness |
| Modelling | `trained_model` — Conv1D with BatchNorm, logged to MLflow |
| Evaluation | val_acc curve per epoch; DeepChecks train/test comparison |

## The key pattern

Each pipeline run is a reproducible unit:
- The same code + the same data = the same model
- Changing either produces a new MLflow run with its own ID
- The MLflow run ID links back to the Git commit that pointed DVC at the training data

## What is next

[Lab 6 — Evidently]({{< relref "../06-evidently" >}}) goes deeper into the monitoring side: running Evidently against live predictions, detecting drift over time, and understanding when to trigger a new Dagster run.
