---
title: "Setup"
weight: 2
---

## Start the services

```bash
./scripts/start.sh mlflow
./scripts/start.sh jupyterlab
```

JupyterLab takes about 15 seconds to start. When ready, the start script prints:

```
  JupyterLab  http://localhost:{{< port "jupyter_port" >}}/?token=<JUPYTER_TOKEN>
```

Copy the full URL including the token and open it in your browser.

{{% notice style="warning" %}}
The token is in `services/jupyterlab/.env` as `JUPYTER_TOKEN`. If you lose the URL, run:
```bash
cat services/jupyterlab/.env | grep JUPYTER_TOKEN
```
{{% /notice %}}

## Interface tour

When JupyterLab opens you will see a launcher on the right and a file browser on the left.

**File browser** — the `notebooks/` folder in the left panel maps to the repo's `notebooks/` directory on disk. Notebooks you save here are saved to Git.

**Launcher** — click **Python 3 (ipykernel)** to open a new notebook, or **Terminal** for a shell inside the container.

**Kernels** — each open notebook runs its own Python process. Variables are not shared between notebooks unless you explicitly pass them.

## Verify MLflow connection

Open a new notebook and run:

```python
import mlflow, os
print("Tracking URI:", os.environ.get("MLFLOW_TRACKING_URI"))
mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
print("Connected:", mlflow.get_tracking_uri())
```

You should see `http://host.docker.internal:{{< port "mlflow_port" >}}` printed. If MLflow is not running, start it now — the notebook will still open, but logging calls will fail silently until the server is available.

{{% expand title="Start here if you skipped earlier labs" %}}
Start MLflow before continuing:
```bash
./scripts/start.sh mlflow
```
No prior training run is required for this lab.
{{% /expand %}}
