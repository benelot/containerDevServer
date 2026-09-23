---
title: "Lab 4 — Label Studio"
weight: 4
---

## Data annotation closes the CRISP-DM loop

A model deployed to production will encounter data the training set never covered. Label Studio is where new data gets human labels before it re-enters the pipeline.

In this lab you will:

1. Start Label Studio and create a labeling project for MNIST 1D sequences
2. Import raw samples and annotate their digit classes
3. Export the annotations, track the result with DVC, and understand how this triggers a new training run in Dagster

### Services used in this lab

| Service | Purpose |
|---|---|
| Label Studio | Annotation UI and project management |
| DVC / MinIO | Version the annotated export |

```bash
./scripts/start.sh label-studio
./scripts/start.sh dvc
```

### CRISP-DM connection

This lab covers the **Data Understanding** and **Data Preparation** phases. Every annotation session produces a new, versioned dataset that feeds back into the pipeline — the core of the CRISP-DM iteration.
