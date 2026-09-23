---
title: "Setup"
weight: 2
---

## Start the service

```bash
./scripts/start.sh evidently
```

The Evidently UI opens at **{{< svcurl "evidently_port" >}}**.

Verify it is healthy:

```bash
curl {{< svcurl "evidently_port" >}}/health
# → {"status":"ok"}
```

## Install the Evidently Python package

Evidently is driven by Python scripts that you run on your host machine (or in JupyterLab). The UI just displays the reports those scripts upload.

```bash
pip install "evidently>=0.4"
```

## Create a project in the UI

1. Open **{{< svcurl "evidently_port" >}}**.
2. Click **New Project**.
3. Name it `mnist1d-monitoring`.
4. The project is now visible in the sidebar. Click it to see its (empty) report history.

Alternatively, create the project from Python — which is how the pipeline does it:

```python
from evidently.ui.workspace import Workspace

ws = Workspace(url="{{< svcurl "evidently_port" >}}")
project = ws.create_project("mnist1d-monitoring")
project.description = "MNIST 1D drift monitoring"
project.save()
print("Project ID:", project.id)
```

Save the project ID — you will need it to push reports.

{{% expand title="Start here if you skipped earlier labs" %}}
Only Evidently is required for this lab. No prior dataset or model is needed — the reference and current data are generated here.
```bash
pip install "evidently>=0.4" mnist1d
./scripts/start.sh evidently
```
{{% /expand %}}
