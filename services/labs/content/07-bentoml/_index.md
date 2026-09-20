---
title: "Lab 7 — BentoML"
weight: 7
---

## The serving layer

A trained model only has value if something can call it. BentoML turns the PyTorch model registered in MLflow into a REST API with a single `predict` endpoint.

In this lab you will:

1. Start BentoML and confirm it loaded the Production model from MLflow
2. Send MNIST 1D sequences to the `/predict` endpoint
3. Understand the request/response format and the degraded-mode fallback

### Services used in this lab

| Service | Purpose |
|---|---|
| BentoML | Serve the model as a REST API |
| MLflow | Provide the Production model at startup |

```bash
./scripts/start.sh bentoml
./scripts/start.sh mlflow
```

### CRISP-DM connection

BentoML covers the **Deployment** phase. It is also the source of the live predictions that Evidently monitors — closing the loop back to **Data Understanding**.
