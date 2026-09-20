# Evidently

## What it does

[Evidently](https://www.evidentlyai.com) is an open-source ML observability platform. It generates interactive reports and test suites that answer the question: "is the data or model behaviour in production still what I expected when I trained it?"

Core capabilities:

- **Data quality reports** -- null rates, distribution summaries, value range violations
- **Data drift detection** -- statistical tests to flag when production data has shifted away from the training distribution
- **Model performance monitoring** -- track accuracy, precision, recall, and custom metrics over time as new ground truth arrives
- **Test suites** -- define pass/fail thresholds and run them on a schedule; results appear in the UI as a timeline

## Architecture in this stack

The container runs the Evidently UI server (`evidently ui`) backed by a named Docker volume (`evidently_workspace`). The workspace holds JSON snapshot files. Snapshots are pushed from Python code (notebooks or the Dagster pipeline) using the Evidently SDK.

```python
from evidently.ui.workspace import Workspace
ws = Workspace("http://localhost:8001")
ws.add_run(project_id, report)
```

The UI then renders these snapshots as an interactive dashboard with time-series panels.

This service runs standalone. It does not share a database with other services. All state is in the named volume, which survives container restarts and can be backed up with a single volume copy.

Port 8001 is used (rather than the default 8000) so the service can run alongside other web services on the same host without conflict.

## Default ports

| Service | Port | Variable |
|---|---|---|
| Evidently UI | 8001 | `EVIDENTLY_PORT` |

## Quick start

```bash
./scripts/start.sh evidently
# Open http://localhost:8001
# Push a snapshot from a notebook or the Dagster pipeline to see data in the UI
```

Minimal Python example:

```python
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataQualityPreset, DataDriftPreset
from evidently.ui.workspace import Workspace

reference = pd.DataFrame(...)  # training data
current   = pd.DataFrame(...)  # new production data

report = Report(metrics=[DataQualityPreset(), DataDriftPreset()])
report.run(reference_data=reference, current_data=current)

ws = Workspace("http://localhost:8001")
project = ws.create_project("my_model")
ws.add_run(project.id, report)
```

## CRISP-DM role

Evidently is the primary tool for the **Evaluation** and **Deployment** phases, and specifically for the feedback loop that connects Deployment back to Business Understanding.

| Phase | What Evidently provides |
|---|---|
| Evaluation | Generate quality and drift reports at the end of each training pipeline run to confirm the dataset is sound |
| Deployment | Monitor incoming production data for distribution shift that would degrade the deployed model |
| Deployment | Alert when drift exceeds a threshold, triggering a re-labeling cycle in Label Studio and retraining in Dagster |
| Business Understanding | Surface degradation to stakeholders via the UI before it causes visible product failures |

Without monitoring, the Deployment phase is the end of the cycle. With Evidently, production observations flow back as the starting conditions for the next iteration, closing the CRISP-DM loop.
