---
title: "Troubleshooting"
weight: 5
---

## Common issues

### `Workspace(url=...)` raises "Connection refused"

The Evidently container is not running or the port is wrong. Check:

```bash
docker compose -f services/evidently/docker-compose.yml ps
curl {{< svcurl "evidently_port" >}}/health
```

If the container is stopped, start it:

```bash
./scripts/start.sh evidently
```

### `ws.add_run()` raises `AttributeError: 'Workspace' has no attribute 'add_run'`

You are using an older Evidently version that uses `ws.add_report()`. Upgrade:

```bash
pip install "evidently>=0.4" --upgrade
```

The current API is `ws.add_run(project_id, report)`.

### Report pushes succeed but the UI shows nothing

The UI polls for new runs every few seconds. Wait 5–10 seconds and refresh. If the project still shows zero runs, verify the `project.id` you passed matches the one in the UI URL: `{{< svcurl "evidently_port" >}}/projects/<id>`.

To list all projects from Python:

```python
from evidently.ui.workspace import Workspace
ws = Workspace(url="{{< svcurl "evidently_port" >}}")
for p in ws.list_projects():
    print(p.id, p.name)
```

### `DataDriftPreset` reports all features as "not drifted" even with high noise

The default drift test requires enough samples to achieve statistical power. With fewer than ~100 samples per dataset the test may not detect drift even when the distributions look visually different. Use at least 500 samples for reliable results:

```python
args.n_samples = 2000   # more samples → stronger statistical test
```

### The Evidently workspace volume is corrupted

If the UI shows errors on startup, the workspace volume may be inconsistent. Reset it:

```bash
docker compose -f services/evidently/docker-compose.yml down -v
./scripts/start.sh evidently
```

This deletes all stored projects and reports. Re-create the project and re-push the reports.
