# JupyterLab

## What it does

[JupyterLab](https://jupyterlab.readthedocs.io) is an interactive development environment for notebooks, code, and data. It runs in the browser and supports Python, R, and Julia kernels out of the box.

In this stack JupyterLab is the primary workspace for:

- Exploratory data analysis (EDA) and visualisation
- Prototyping model architectures
- Running training experiments while logging to MLflow
- Producing the CRISP-DM walkthrough notebook (`notebooks/mnist1d_crisp_dm.ipynb`)
- Running the data quality notebook (`notebooks/data_quality.ipynb`)

## Architecture in this stack

The image used is `jupyter/datascience-notebook`, which includes Python (with common scientific packages), R, and Julia in a single container. The `JUPYTER_IMAGE` variable in `.env` can be changed to a lighter image if R and Julia are not needed.

Several configuration choices are intentional:

**`extra_hosts: host.docker.internal:host-gateway`**
On Linux, containers cannot resolve `host.docker.internal` by default. This line injects the host's gateway IP under that name so that notebooks can reach MLflow (`http://host.docker.internal:5000`) and MinIO (`http://host.docker.internal:9000`) without knowing the host's actual IP address.

**`user: root` and `GRANT_SUDO: "yes"`**
Required to install packages at runtime with `pip install` or `apt-get` inside the container. This is safe for a local development environment and avoids the friction of rebuilding the image for each new dependency.

**`../../notebooks:/home/jovyan/notebooks`**
The repo's `notebooks/` directory is bind-mounted into the container. Notebooks are saved directly to the repo and can be committed to Git. This removes the risk of losing work when the container is recreated.

**MLflow and MinIO environment variables**
`MLFLOW_TRACKING_URI`, `MLFLOW_S3_ENDPOINT_URL`, and AWS credentials are injected at startup so that `import mlflow; mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])` works immediately without any manual configuration in the notebook.

## Default ports

| Service | Port | Variable |
|---|---|---|
| JupyterLab | 8888 | `JUPYTER_PORT` |

Access URL: `http://localhost:8888/?token=<JUPYTER_TOKEN>`

## Quick start

```bash
./scripts/start.sh jupyterlab
# Open the URL printed by the script
# Notebooks are in ~/notebooks (bound to the repo's notebooks/ directory)
```

## CRISP-DM role

JupyterLab spans the first four phases of CRISP-DM. It is where the iterative, exploratory work happens before anything is promoted to a production pipeline.

| Phase | What JupyterLab provides |
|---|---|
| Business Understanding | Write down the problem definition and success criteria in a notebook cell before touching any data |
| Data Understanding | Load, visualise, and describe the dataset; identify outliers, class imbalance, and missing values |
| Data Preparation | Prototype cleaning and feature engineering code that will later be productionised in Dagster |
| Modelling | Iterate quickly on architecture and hyperparameters; every run is logged to MLflow |
| Evaluation | Inspect predictions, plot confusion matrices, and explore failure cases interactively |

Notebooks are the scratchpad. Once a process is validated and understood in a notebook, it moves to a Dagster asset for reliable, scheduled execution.
