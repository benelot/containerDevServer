# Evidently

Data drift and model quality monitoring UI for the CRISP-DM Evaluation and Deployment phases.

## CRISP-DM role

| Phase | Contribution |
|---|---|
| Evaluation | Generate rich HTML reports comparing training data to new data; surface distribution shifts before they affect production |
| Deployment | Persist monitoring snapshots over time; track model and data quality trends across deployments |

Evidently bridges pipeline validation and post-deployment monitoring. The same report format works both as a one-shot evaluation artifact (logged to MLflow during a Dagster pipeline run) and as a persistent time-series dashboard in the Evidently UI.

## How it works

Evidently distinguishes between **reports** (HTML documents with metrics and visualisations) and **test suites** (pass/fail assertions against thresholds). Both can be saved locally or pushed as JSON snapshots to the Evidently service workspace, where they accumulate into a monitoring dashboard.

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

report = Report(metrics=[DataQualityPreset(), DataDriftPreset()])
report.run(reference_data=df_train, current_data=df_production)
report.save_html("drift_report.html")

# Push to the monitoring service
from evidently.ui.workspace import Workspace
ws = Workspace(url="http://localhost:8001")
ws.add_run(project_id, report)
```

## Integration with the stack

- **Dagster pipeline** — `data_quality_report` generates Evidently reports on every run and logs them to MLflow as artifacts.
- **Notebooks** — `notebooks/data_quality.ipynb` generates standalone HTML reports and optionally pushes snapshots to the monitoring service.
- **BentoML** — prediction logs can be formatted as Evidently snapshots and pushed to the workspace for production drift monitoring.

## Quickstart

```bash
./scripts/start.sh evidently
# http://localhost:8001
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `EVIDENTLY_PORT` | `8001` | Evidently UI port |
