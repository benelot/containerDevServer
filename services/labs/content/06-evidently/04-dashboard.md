---
title: "Dashboard"
weight: 4
---

## Reading the Evidently UI

After pushing several reports, the project dashboard shows:

- **Run list** — each pushed report as a timestamped row
- **Metric panels** — configurable charts for any logged metric across runs
- **Per-run detail** — the full HTML report for any individual run

### Setting up a drift score panel

In the project view, click **Add Panel** → **Counter** or **Line Chart**.

Select the metric `DatasetDriftMetric / share_of_drifted_columns`. This shows the fraction of the 40 features that crossed the drift threshold in each run.

With your three-run batch you should see a rising trend: 0.2 noise → low fraction, 0.6 noise → high fraction.

## Drift thresholds and decisions

Evidently uses a statistical test per feature (Jensen-Shannon divergence for numerical features by default). A feature is marked as "drifted" when the test statistic exceeds `0.1` by default.

You can adjust this per-report:

```python
from evidently.metrics import DataDriftTable
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[
    DataDriftPreset(drift_share=0.2)   # alert if >20% of features drift
])
```

A common operational rule: if `share_of_drifted_columns > 0.3` trigger a Label Studio annotation batch. Codify this as a Dagster sensor later.

## Connecting drift to retraining

The loop is:

```
Evidently drift score > threshold
        │
        ▼
  Open Label Studio project for new batch
        │
        ▼
  Export annotations → DVC version
        │
        ▼
  Trigger Dagster mnist1d_full_pipeline
        │
        ▼
  New model version in MLflow
        │
        ▼
  BentoML serves new version
        │
        ▼
  Evidently monitors again (drift should fall)
```

Each iteration leaves a traceable trail: every model version in MLflow has a run ID that links to the Git commit that links to the DVC-tracked dataset that links to the Label Studio project.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Open the Evidently UI and confirm all your pushed runs are visible
- [ ] Add a `share_of_drifted_columns` line chart panel to your project
- [ ] Identify the noise level at which more than 30% of features drift
- [ ] Document (in a notebook comment) what action you would take at that threshold
{{% /notice %}}
