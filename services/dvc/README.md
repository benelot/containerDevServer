# DVC Remote Cache

## What it does

[DVC](https://dvc.org) (Data Version Control) adds Git-like versioning to datasets and large files. It stores the actual bytes in a remote cache and commits only a small `.dvc` pointer file to Git. This gives you:

- **Reproducibility** -- check out any Git commit and `dvc pull` to restore the exact dataset that commit used
- **Lineage** -- trace a model back to the specific dataset version it was trained on
- **Deduplication** -- content-addressed storage means unchanged files are never uploaded twice

## Architecture in this stack

This service runs a MinIO instance that acts as the DVC remote. MinIO is a self-hosted S3-compatible object store. DVC talks to it with the standard S3 protocol, so the configuration is identical to an AWS S3 remote -- only the endpoint URL differs.

A dedicated MinIO instance (ports 9010/9011) is used instead of sharing with the MLflow MinIO. The reasons are:

- **Isolation** -- DVC data and MLflow artifacts have different access patterns and retention policies
- **Independent scaling** -- each store can be moved to a larger disk or a real S3 bucket without touching the other
- **No port conflict** -- both stacks can run simultaneously on the same host

## Default ports

| Service | Port | Variable |
|---|---|---|
| MinIO S3 API | 9010 | `MINIO_API_PORT` |
| MinIO Console | 9011 | `MINIO_CONSOLE_PORT` |

## Quick start

```bash
./scripts/start.sh dvc

# Configure DVC remote once in your project repo:
dvc remote add -d myremote s3://dvc-cache
dvc remote modify myremote endpointurl http://localhost:9010
dvc remote modify myremote access_key_id minioadmin
dvc remote modify myremote secret_access_key minioadmin_secret

# Version a dataset:
dvc add data/raw/mnist1d.pkl
git add data/raw/mnist1d.pkl.dvc .gitignore
git commit -m "add raw MNIST 1D dataset"
dvc push
```

## CRISP-DM role

DVC covers the **Data Understanding** and **Data Preparation** phases, and underpins reproducibility across the entire cycle.

| Phase | What DVC provides |
|---|---|
| Data Understanding | Tag and version the raw dataset at the moment you first explore it; exploration is then always reproducible |
| Data Preparation | Version each cleaned or transformed dataset separately so preprocessing steps can be compared or rolled back |
| Modelling | Pin the exact data version used to train each experiment, complementing MLflow's parameter logging |
| Deployment | Re-create any historical training run by checking out the matching Git commit and running `dvc pull` |

DVC answers the question "what data was this model trained on?" even months after the fact.
