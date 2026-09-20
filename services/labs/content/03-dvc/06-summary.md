---
title: "Summary"
weight: 6
---

## What you did

- Started a MinIO-backed DVC remote
- Generated two variants of the MNIST 1D dataset with different noise levels
- Tracked both with DVC and committed the pointer files to Git
- Restored an earlier dataset version using `git checkout` + `dvc pull`

## CRISP-DM phases covered

| Phase | How DVC contributes |
|---|---|
| Data Preparation | Every cleaned or transformed dataset is a versioned DVC artifact |
| Modelling | Pin the exact dataset version used for each experiment — link MLflow run ID to Git commit |
| Deployment | New annotated data from Label Studio becomes a new DVC version; the retraining pipeline references it explicitly |

## The key command pair

```bash
# Save a new version
dvc add data/dataset.pkl
git add data/dataset.pkl.dvc && git commit -m "Dataset v3"
dvc push

# Restore any version
git checkout <commit> -- data/dataset.pkl.dvc
dvc pull
```

## What is next

[Lab 4 — Label Studio]({{< relref "../04-label-studio" >}}) is where new data enters the system. You will set up a labeling project for MNIST 1D sequences, annotate a few samples, and export the result as a DVC-tracked dataset ready for the pipeline.
