---
title: "Lab 1 — MLflow"
chapter: true
weight: 2
pre: "<b>Lab 1. </b>"
---

# Lab 1 — MLflow

**Experiment tracking and model registry.**

Every time you train a model you make dozens of decisions: learning rate, batch size, architecture, preprocessing steps. Without a tracker, you lose those decisions the moment you close your notebook. MLflow records every run automatically so you can compare, reproduce, and share your experiments.

By the end of this lab you will have:
- A running MLflow server backed by PostgreSQL and MinIO
- Your first tracked training run with parameters, metrics, and a saved model
- A model registered in the Model Registry and promoted to Production

**Services needed for this lab:** MLflow only.

```bash
./scripts/start.sh mlflow
```
