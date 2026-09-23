---
title: "Concept"
weight: 1
---

## The data versioning problem

Imagine you trained a model six months ago, the results were excellent, and a customer now wants to reproduce them. You check out the exact Git commit. You run the notebook. The results are different.

Why? The dataset changed. A preprocessing script was re-run, samples were added or removed, a label was corrected. The code is identical but the data is not, and you have no record of what the data looked like when the original training ran.

DVC solves this by extending the Git model to large files.

## How DVC works

DVC replaces large files (datasets, model checkpoints, anything too big for Git) with small pointer files called `.dvc` files. The pointer contains a content hash:

```yaml
# data/mnist1d_data.pkl.dvc
md5: a3f8c2...
size: 45192
path: mnist1d_data.pkl
```

The `.dvc` file is tiny — it goes into Git. The actual data goes to a remote storage backend (MinIO in this stack). When you need the data, you run `dvc pull` and DVC downloads exactly the version the pointer references.

Because the pointer is in Git, `git checkout <old-commit>` retrieves the old pointer, and `dvc pull` retrieves the exact dataset that existed at that commit.

## DVC vs MLflow artifacts

Both tools store large files. The distinction is purpose:

| | DVC | MLflow |
|---|---|---|
| What it stores | Raw and processed datasets | Training artifacts: models, reports, plots |
| Versioning trigger | Git commit | MLflow run |
| Typical content | `mnist1d_data.pkl`, `features.parquet` | `model.pth`, `confusion_matrix.png` |

Use DVC for the inputs to training. Use MLflow for the outputs.

## The DVC remote in this stack

The DVC service runs a dedicated MinIO instance on ports {{< port "dvc_minio_port" >}}/{{< port "dvc_minio_console_port" >}}. It is intentionally separate from the MLflow MinIO (ports {{< port "mlflow_minio_port" >}}/{{< port "mlflow_minio_console_port" >}}) so you can apply different backup policies and retention rules to each store. Switching either to real AWS S3 requires changing only the endpoint URL.
