---
title: "Troubleshooting"
weight: 5
---

## Common issues

### Cannot open the JupyterLab URL — "Invalid credentials"

The token in the URL must match `JUPYTER_TOKEN` in `services/jupyterlab/.env`. If you changed the token after starting the container, restart the stack:

```bash
./scripts/start.sh jupyterlab --stop
./scripts/start.sh jupyterlab
```

### `pip install` inside a notebook fails with "Permission denied"

The container runs as root by default. If you see permission errors, check whether the container is running a different image (some images create a non-root `jovyan` user). The compose file in this stack adds `--user root` to ensure installs work.

### MLflow logging fails silently — runs do not appear

Check that `MLFLOW_TRACKING_URI` is set in the notebook's environment:

```python
import os
print(os.environ.get("MLFLOW_TRACKING_URI"))
# should print http://host.docker.internal:{{< port "mlflow_port" >}}
```

If it is not set, set it manually and check that the MLflow server is running:

```python
import mlflow
mlflow.set_tracking_uri("{{< svcurl "mlflow_port" >}}")
```

### The notebook raises `ModuleNotFoundError` for `mnist1d`

`mnist1d` is not in the base datascience-notebook image. Install it:

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "mnist1d"])
```

The `mnist1d_crisp_dm.ipynb` notebook includes this install cell at the top.

### Kernel dies during training

The datascience-notebook container has unlimited memory by default. If the Docker daemon has a memory limit set, the kernel OOM-kills during the large matrix operations. Increase Docker's memory allocation in Docker Desktop → Settings → Resources.

### Changes to notebooks are not saved to disk

The `notebooks/` directory in the container is a bind mount to `notebooks/` in the repo root. Saves inside JupyterLab write directly to the host filesystem. If saves are not persisting, check that the mount succeeded:

```bash
docker compose -f services/jupyterlab/docker-compose.yml exec jupyterlab \
  ls /home/jovyan/work/notebooks/
```
