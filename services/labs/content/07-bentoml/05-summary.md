---
title: "Summary"
weight: 5
---

## What you did

- Started BentoML and confirmed it loaded the Production model from MLflow
- Sent individual and batch sequences to the `/predict` endpoint
- Used the MNIST 1D generator to create test sequences at varying noise levels
- Collected prediction logs that can feed back into Evidently drift monitoring

## CRISP-DM phases covered

| Phase | How BentoML contributes |
|---|---|
| Deployment | REST API makes the model accessible to any client without Python dependencies |
| Evaluation | Prediction logs captured at serving time feed back into drift monitoring |

## The key pattern

```python
import requests
resp = requests.post(
    "http://localhost:{{< port "bentoml_port" >}}/predict",
    json={"sequences": X.tolist()}
)
preds = resp.json()["predictions"]
probs = resp.json()["probabilities"]
```

Promote a new model version in MLflow → restart BentoML → the new model is live. No code changes, no redeployment.

## What is next

[Lab 8 — Monitoring]({{< relref "../08-monitoring" >}}) is the infrastructure layer: Prometheus scrapes metrics from every service, Grafana visualises them, and you will configure dashboards that show the health of the entire stack at a glance.
