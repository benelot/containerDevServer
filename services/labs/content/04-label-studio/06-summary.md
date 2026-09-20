---
title: "Summary"
weight: 6
---

## What you did

- Created a Label Studio project with a custom XML label configuration for digit classification
- Imported 20 MNIST 1D sequence samples as annotation tasks
- Annotated all tasks and exported the result as a JSON file
- Converted the export to a training-ready `.pkl` file
- Tracked the annotated batch with DVC and versioned it in Git

## CRISP-DM phases covered

| Phase | How Label Studio contributes |
|---|---|
| Data Understanding | Human review of raw sequences surfaces labeling ambiguity and distribution gaps |
| Data Preparation | Annotations become a DVC-versioned dataset with a Git commit linking data to model |
| Evaluation | Inter-annotator agreement and confidence scores measure label quality |
| Deployment | Drift-flagged samples from the live model feed back into Label Studio for the next batch |

## The export–track–train cycle

```bash
# Export from Label Studio UI → save to disk, then:
dvc add data/annotated_batch_v1.pkl
git add data/annotated_batch_v1.pkl.dvc && git commit -m "Annotated batch v1"
dvc push
# Trigger Dagster pipeline → new MLflow run referencing this commit
```

## What is next

[Lab 5 — Dagster]({{< relref "../05-dagster" >}}) is the pipeline that turns annotated data into a trained model. You will walk through every asset in the pipeline: Pandera schema validation, DeepChecks data integrity, Conv1D training, and Evidently drift reporting — each step a CRISP-DM phase made concrete.
