---
title: "Concept"
weight: 1
---

## What MLflow tracks

MLflow organises everything about a training run into four concepts:

**Experiments** group related runs together. You might have one experiment per dataset or one per modelling approach. Runs inside an experiment are listed side by side so you can compare them.

**Runs** are individual training executions. Each run has a unique ID, a start/end time, and a status. Inside a run you store parameters, metrics, and artifacts.

**Parameters** are the inputs to your run: hyperparameters (`lr=0.001`), configuration choices (`optimizer=adam`), or dataset descriptors (`n_samples=4000`). They are logged once and do not change.

**Metrics** are scalar values that can be logged at every step: `val_acc`, `train_loss`, `f1_score`. MLflow plots them as time-series so you can see how they evolve across epochs.

**Artifacts** are any files you want to keep: model weights, plots, HTML reports, confusion matrices. MLflow stores them in MinIO (an S3-compatible object store) and links them to the run.

## The Model Registry

Beyond tracking runs, MLflow maintains a **Model Registry** — a versioned catalogue of model artifacts with lifecycle stages.

```
Run ──► register ──► Registered Model
                           │
                    ┌──────┴──────┐
                    │             │
                 Staging      Production
                    │             │
                 (testing)   (serving)
```

When a training run produces a model you want to keep, you register it under a name (e.g. `mnist1d-conv1d`). Each registration creates a new version. You then promote versions through stages:

- **Staging** — validated, ready for review
- **Production** — live; BentoML loads this version on startup
- **Archived** — superceded, kept for audit

BentoML always loads the `Production` version of `mnist1d-conv1d`. Promoting a new model in MLflow and restarting BentoML is all it takes to deploy an update.

## Why PostgreSQL and MinIO?

MLflow supports SQLite for the backend store and local files for artifacts, which works fine on a laptop. This stack uses **PostgreSQL** and **MinIO** instead, for two reasons:

1. PostgreSQL supports concurrent writers. Both the Dagster pipeline and a JupyterLab notebook can log runs simultaneously without locking.
2. MinIO is an S3-compatible object store. Moving to AWS S3 later requires changing only an endpoint URL — no code changes.

The `--serve-artifacts` flag on the MLflow server means clients never talk directly to MinIO. All artifact traffic goes through the MLflow HTTP API, so you do not need to configure S3 credentials in every notebook.
