---
title: "Concept"
weight: 1
---

## What Evidently measures

Evidently compares two datasets — a **reference** (your training data) and **current** (recent predictions or new batches) — and reports statistical differences.

### Key terms

| Term | Meaning |
|---|---|
| **Reference data** | The baseline, usually the training set |
| **Current data** | New data to compare against the baseline |
| **Drift score** | A per-feature statistic (0 = identical distribution, 1 = completely different) |
| **Report** | A single comparison run, saved as an HTML file or a JSON snapshot |
| **Project** | A named collection of reports with a shared workspace |
| **Preset** | A pre-built set of metrics (e.g. `DataDriftPreset`, `DataQualityPreset`) |

### Why drift matters

A model trained on clean, low-noise MNIST 1D data will degrade when deployed in an environment where noise increases, sensors drift, or the class balance shifts. Without monitoring, you learn about degradation from user complaints or a sudden accuracy drop — after the damage is done.

Evidently makes drift visible proactively, on a schedule, so you can act before model quality visibly degrades.

### The three questions Evidently answers

1. **Data quality:** Are there missing values, constant columns, or out-of-range values in the new batch?
2. **Data drift:** Has the feature distribution shifted significantly from training?
3. **Prediction drift:** Is the model's output distribution changing? (Requires logging predictions alongside inputs.)

### How it fits the stack

```
BentoML serving predictions
        │
        ▼
  Collect live inputs + predictions
  (logged to a file, a database, or a queue)
        │
        ▼
  Evidently: compare to training reference
        │
        ├── No significant drift → continue monitoring
        │
        └── Drift detected
                │
                ▼
          Alert → Label Studio: annotate flagged samples
                │
                ▼
          DVC: version the new annotated batch
                │
                ▼
          Dagster: retrain pipeline
```
