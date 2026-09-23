---
title: "Stack overview"
weight: 2
---

## The eight services

Each service in the stack handles a specific part of the CRISP-DM cycle. They are designed to run simultaneously on a single machine and talk to each other over a shared Docker network.

| Service | Port | CRISP-DM phase | Role |
|---|---|---|---|
| **MLflow** | {{< port "mlflow_port" >}} | Modelling, Evaluation, Deployment | Experiment tracker, artifact store, model registry |
| **JupyterLab** | {{< port "jupyter_port" >}} | All phases | Interactive exploration and prototyping |
| **DVC** (MinIO) | {{< port "dvc_minio_port" >}} | Data Preparation | Dataset and artifact versioning |
| **Label Studio** | {{< port "label_studio_port" >}} | Data Understanding, Deployment | Data annotation and retraining feedback loop |
| **Dagster** | {{< port "dagster_port" >}} | Data Preparation, Modelling, Evaluation | Pipeline orchestration |
| **Evidently** | {{< port "evidently_port" >}} | Evaluation, Deployment | Data drift and model quality monitoring |
| **BentoML** | {{< port "bentoml_port" >}} | Deployment | Model serving (REST API) |
| **Monitoring** | {{< port "grafana_port" >}} | Deployment | Hardware health, service uptime, GPU metrics |

## The MNIST 1D dataset

All labs use MNIST 1D: a compact, synthetic dataset designed as a drop-in replacement for MNIST that runs on CPU in seconds. Each sample is a 40-point 1D time-series representing one of ten digit classes (0–9). The full dataset has 4000 training samples and 1000 test samples.

```python
from mnist1d.data import make_dataset, get_dataset_args

args = get_dataset_args()   # default: seed=42, num_samples=4000
data = make_dataset(args)

print(data['x'].shape)       # (4000, 40)  — training sequences
print(data['y'].shape)       # (4000,)     — training labels
print(data['x_test'].shape)  # (1000, 40)  — test sequences
```

The generator is the key feature for these labs. Because you can recreate the dataset from scratch in seconds with a single function call, every lab is independent — you never need a previous lab to have run successfully.

Changing `args.seed`, `args.noise_scale`, or `args.padding` produces datasets with different properties, which is how the Evidently and Dagster labs demonstrate drift detection and data validation failures.

## How the tools connect

```
Label Studio ──► DVC ──► Dagster pipeline
                              │
                    ┌─────────┼────────────┐
                    │         │            │
                 Pandera   DeepChecks  Evidently
                 (validate) (integrity) (drift)
                              │
                           MLflow ──► BentoML ──► Monitoring
                          (track)     (serve)     (observe)
```

The pipeline orchestrated by Dagster is the spine of the workflow:
1. **Pandera** validates the incoming data schema
2. **DeepChecks** checks train/test distribution and data integrity
3. **Evidently** generates drift and quality reports
4. The **Conv1D model** is trained and all metrics are logged to **MLflow**
5. The registered model is served by **BentoML**
6. **Monitoring** (Prometheus + Grafana) tracks everything above

## Starting services

Each lab tells you exactly which services to start. You never need more than two or three running at once. Start them with:

```bash
./scripts/start.sh mlflow
./scripts/start.sh jupyterlab
# etc.
```

On first run, the script copies `.env.example` to `.env` and prints the service URLs. Default ports work with no configuration. If you share a machine with other users, run `./scripts/generate-ports.sh` first to get a unique port block.
