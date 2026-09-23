---
title: "Summary"
weight: 6
---

## What you did

- Started the Evidently UI and created a monitoring project
- Generated reference and current MNIST 1D datasets with varying noise levels
- Ran drift reports and pushed them to the Evidently UI
- Read the drift score trend across multiple batches
- Connected the drift threshold to the decision to retrain

## CRISP-DM phases covered

| Phase | How Evidently contributes |
|---|---|
| Deployment | Continuous monitoring of live predictions against training distribution |
| Business Understanding | Drift alerts translate statistical signals into retraining decisions |
| Data Understanding | Each drift report surfaces which features are changing and by how much |

## The key pattern

```python
# Minimal monitoring run
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.ui.workspace import Workspace

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=ref, current_data=current_batch)

ws = Workspace(url="http://localhost:{{< port "evidently_port" >}}")
ws.add_run(project_id, report)
```

## What is next

[Lab 7 — BentoML]({{< relref "../07-bentoml" >}}) is where the trained model becomes an API. You will load the Production model from the MLflow registry, send MNIST 1D sequences to the REST endpoint, and understand how BentoML integrates into the full prediction loop.
