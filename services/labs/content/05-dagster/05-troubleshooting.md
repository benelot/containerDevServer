---
title: "Troubleshooting"
weight: 5
---

## Common issues

### Dagster UI shows no assets

The webserver and daemon must both be running. Check:

```bash
docker compose -f services/dagster/docker-compose.yml ps
```

Both `dagster-webserver` and `dagster-daemon` should be `Up`. If the daemon is not running, scheduled jobs and sensors will not fire:

```bash
docker compose -f services/dagster/docker-compose.yml restart dagster-daemon
```

### `raw_dataset` fails with "connection reset" or timeout

The asset downloads from GitHub. In an offline or restricted network, the download will fail. Pre-download the file manually and place it at the cache path:

```bash
docker exec -it <dagster-container> bash
curl -L https://github.com/greydanus/mnist1d/raw/master/mnist1d_data.pkl \
     -o /tmp/mnist1d_data.pkl
```

Then re-materialise — the asset will skip the download and use the cache.

### `validated_dataset` fails with `SchemaError`

Pandera found a row that violates the schema. The error message includes the column name and the offending value. Common causes:

- A label outside 0–9 (from a custom annotation batch)
- Feature values outside `[-8.0, 8.0]` (from a badly scaled custom dataset)

To inspect which rows fail:

```python
import pandera as pa, pandas as pd, pickle, numpy as np
with open("data/mnist1d_data.pkl", "rb") as f:
    d = pickle.load(f)
df = pd.DataFrame(d["x"], columns=[f"t{i}" for i in range(40)])
df["label"] = d["y"]
# find offending rows:
print(df[(df < -8.0).any(axis=1) | (df > 8.0).any(axis=1)])
```

### `data_quality_report` logs "Could not log to MLflow"

The MLflow container is not running or `MLFLOW_TRACKING_URI` points to the wrong host. The asset continues and produces HTML reports at `/tmp/`, but they are not uploaded to MLflow. Start MLflow:

```bash
./scripts/start.sh mlflow
```

Then re-materialise only the `data_quality_report` asset (right-click → Materialise).

### `trained_model` asset runs but no model appears in the registry

Check the MLflow logs in the Dagster run for a `WARNING` about the tracking URI. If it logged a warning and skipped registration, the model was trained but not registered. Fix the URI and re-materialise `trained_model`.

### Run is stuck — asset shows "In Progress" indefinitely

The Dagster daemon may have crashed. Restart it:

```bash
docker compose -f services/dagster/docker-compose.yml restart dagster-daemon
```

If the run cannot be cancelled from the UI, force-terminate it via the Dagster API:

```bash
curl -X POST {{< svcurl "dagster_port" >}}/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { terminateRun(runId:\"<run-id>\"){__typename}}"}'
```
