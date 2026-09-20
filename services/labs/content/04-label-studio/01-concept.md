---
title: "Concept"
weight: 1
---

## Why a labeling tool?

Raw data collected from a deployed model has no ground-truth labels. Before that data can improve the model, a human must assign correct labels. Label Studio is an open-source tool that organises this work into projects, tracks annotation progress, and exports results in standard formats.

### Key terms

| Term | Meaning |
|---|---|
| **Project** | A labeling task with a defined label set and import/export format |
| **Task** | One item to annotate (one MNIST 1D sequence) |
| **Annotation** | The label(s) a human assigns to a task |
| **Label config** | XML template that tells Label Studio how to display data and what choices to offer |

### How Label Studio fits the pipeline

```
Deployed model
      │
      ▼
 New sequences arrive
      │
      ▼
  Label Studio  ──► annotated JSON
      │
      ▼
   dvc add / git commit
      │
      ▼
  Dagster pipeline  ──► retrained model
      │
      ▼
  MLflow registry  ──► BentoML serves new version
```

The key insight: the DVC pointer file is what ties a specific annotation export to the exact model version trained from it. If the retrained model performs worse you can trace back to exactly which batch of annotations caused it.

### MNIST 1D as a labeling task

Each MNIST 1D sample is a 40-element float array representing a digit (0–9). Label Studio will display the sequence values and ask an annotator to confirm or correct the digit class. This is a **classification** task with a fixed label set of ten classes.

In production the samples fed to Label Studio would come from the confidence-filtered output of the live BentoML service — samples the model was unsure about, collected by the Dagster monitoring pipeline.
