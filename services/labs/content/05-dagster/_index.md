---
title: "Lab 5 — Dagster"
weight: 5
---

## The pipeline that ties everything together

Dagster is the orchestration layer. It turns the manual steps from earlier labs into a reproducible asset graph: fetch data, validate it, check quality, train a model, and register it in MLflow — all in one triggered run.

In this lab you will:

1. Start Dagster and explore the asset graph in its UI
2. Understand each of the four assets: `raw_dataset`, `validated_dataset`, `data_quality_report`, and `trained_model`
3. Trigger a full pipeline run and read its outputs in MLflow

### Services used in this lab

| Service | Purpose |
|---|---|
| Dagster | Pipeline orchestration and asset materialisation |
| MLflow | Experiment logging and model registration |

```bash
./scripts/start.sh dagster
./scripts/start.sh mlflow
```

### CRISP-DM connection

Dagster automates the **Data Preparation → Modelling → Evaluation** arc. Each asset corresponds to one CRISP-DM step, and the graph structure makes the dependencies explicit: you cannot train before you validate, and you cannot deploy without a registered model.
