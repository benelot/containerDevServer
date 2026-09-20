---
title: "Summary"
weight: 6
---

## What you did

- Explored the MNIST 1D dataset with plots and summary statistics
- Understood the generator's parameters and how they affect sample difficulty
- Ran the full CRISP-DM notebook and observed every phase execute
- Compared two training runs with different learning rates in MLflow

## CRISP-DM phases covered

| Phase | How JupyterLab contributes |
|---|---|
| Business Understanding | Document the problem and success criteria in notebook prose cells before writing any code |
| Data Understanding | Explore distributions, visualise samples, identify anomalies interactively |
| Data Preparation | Prototype cleaning steps; validate schema with Pandera before committing to the pipeline |
| Modelling | Iterate quickly on architecture; every run logged automatically |
| Evaluation | Confusion matrix, t-SNE, per-class accuracy — all generated and stored as MLflow artifacts |

## Key pattern

```
Prototype in a notebook → Extract logic → Run in Dagster pipeline
```

The notebook is never the production path. Once you are confident a piece of logic is correct, it belongs in a pipeline asset that can be tested, scheduled, and monitored.

## What is next

[Lab 3 — DVC]({{< relref "../03-dvc" >}}) solves the problem that the notebook currently ignores: the dataset is downloaded fresh each time and never version-controlled. You will track the MNIST 1D dataset with DVC so any version can be reproduced exactly.
