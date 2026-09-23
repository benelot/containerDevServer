# DVC Remote

MinIO S3 remote storage for DVC (Data Version Control) dataset and artifact versioning.

## CRISP-DM role

| Phase | Contribution |
|---|---|
| Data Understanding | Version raw datasets so any snapshot can be restored for re-analysis |
| Data Preparation | Track every cleaned and transformed dataset by content hash |
| Modelling | Pin the exact dataset version used for each experiment |

## Why a dedicated MinIO instance

DVC data and MLflow artifacts live on separate MinIO instances:

- **MLflow MinIO** (ports 9000/9001) — model files, reports, training artifacts
- **DVC MinIO** (ports 9010/9011) — versioned raw and processed datasets

Keeping them separate makes it straightforward to apply different backup policies, retention rules, and access controls to each store. Migrating either to a real AWS S3 bucket later requires changing only the endpoint URL.

## Quickstart

```bash
./scripts/start.sh dvc
```

Configure a DVC project to use this remote:

```bash
dvc remote add -d myremote s3://dvc-cache
dvc remote modify myremote endpointurl http://localhost:9010
dvc remote modify myremote access_key_id minioadmin
dvc remote modify myremote secret_access_key minioadmin_secret
```

Track and push a dataset:

```bash
dvc add data/mnist1d_data.pkl
dvc push
git add data/mnist1d_data.pkl.dvc .gitignore
git commit -m "Track MNIST 1D dataset with DVC"
```

Restore any version:

```bash
git checkout <commit>
dvc pull
```

## Services

| Container | Port | Purpose |
|---|---|---|
| `dvc-minio` | 9010 | MinIO S3 API |
| `dvc-minio` | 9011 | MinIO web console |

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DVC_MINIO_PORT` | `9010` | MinIO S3 API port |
| `DVC_MINIO_CONSOLE_PORT` | `9011` | MinIO web console port |
| `MINIO_ROOT_USER` | `minioadmin` | Access key |
| `MINIO_ROOT_PASSWORD` | `minioadmin_secret` | Secret key |
