---
title: "Concept"
weight: 1
---

## What Dagster orchestrates

Dagster organises work into **assets** — named, versioned outputs with explicit dependencies. When you trigger a job, Dagster executes only the assets that need updating and shows you which materialised successfully and which failed.

### Key terms

| Term | Meaning |
|---|---|
| **Asset** | A named, persistent output (a DataFrame, a model file, a report) |
| **Materialisation** | One execution of an asset's function, producing a new version of the output |
| **Job** | A selected subset of assets executed together |
| **Run** | A single execution of a job, with full logs and metadata |
| **Asset graph** | The visual dependency diagram showing which assets feed which |

### The MNIST 1D asset graph

```
raw_dataset
     │
     ▼
validated_dataset
     │
     ├──────────────────┐
     ▼                  ▼
data_quality_report  trained_model
```

This graph encodes two constraints:
1. You cannot validate data you have not fetched.
2. Quality reporting and model training both depend on validated data, but are independent of each other — Dagster can run them in parallel.

### What each asset does

**`raw_dataset`** — Downloads MNIST 1D from GitHub (or loads a local cache). Returns a dict with `X_train`, `y_train`, `X_test`, `y_test` as NumPy arrays.

**`validated_dataset`** — Converts the arrays to a Pandas DataFrame and runs a Pandera schema against it. The schema checks that each of the 40 feature columns is a float in `[-8.0, 8.0]` and that the `label` column is an integer in `{0, …, 9}`. If any row violates these constraints the asset fails immediately — the downstream assets do not run.

**`data_quality_report`** — Runs two quality frameworks in sequence and logs all results to MLflow:
- **Evidently** generates an HTML report with `DataQualityPreset` (missing values, value ranges, outliers) and `DataDriftPreset` (statistical drift between train and test splits).
- **DeepChecks** runs a `data_integrity` suite on the training set and a `train_test_validation` suite comparing train and test distributions.

**`trained_model`** — Trains a three-layer Conv1D network with BatchNorm, ReLU, and Dropout. Logs hyperparameters and per-epoch validation accuracy to MLflow, then registers the final model as `mnist1d-conv1d`.

### Why this order matters for CRISP-DM

A data quality failure in `validated_dataset` or `data_quality_report` stops the job before wasting training compute. You find out about data problems before you create a model from them — this is the CRISP-DM **Data Understanding** gate.
