---
title: "Drift report"
weight: 3
---

## Generate reference and current datasets

```python
from mnist1d.data import make_dataset, get_dataset_args
import pandas as pd

cols = [f"t{i}" for i in range(40)]

# Reference — clean training data (same as Dagster pipeline)
args_ref = get_dataset_args()
d_ref = make_dataset(args_ref)
ref = pd.DataFrame(d_ref["x"], columns=cols)
ref["label"] = d_ref["y"]

# Current — shifted data simulating production drift
args_cur = get_dataset_args()
args_cur.noise_scale = 0.5   # much noisier than training
args_cur.seed = 123
d_cur = make_dataset(args_cur)
cur = pd.DataFrame(d_cur["x"], columns=cols)
cur["label"] = d_cur["y"]

print("Reference shape:", ref.shape)
print("Current shape:  ", cur.shape)
```

## Run the drift report

```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

report = Report(metrics=[DataQualityPreset(), DataDriftPreset()])
report.run(reference_data=ref, current_data=cur)

# Save local HTML to inspect offline
report.save_html("evidently_drift_report.html")
print("Report saved to evidently_drift_report.html")
```

Open the HTML in your browser. The **Data Drift** section shows one row per feature with a drift score and a pass/fail badge. With `noise_scale=0.5`, most features should show drift.

## Push the report to the Evidently UI

```python
from evidently.ui.workspace import Workspace
import uuid

ws = Workspace(url="{{< svcurl "evidently_port" >}}")

# find your project (or paste the ID from setup)
projects = ws.list_projects()
project = next(p for p in projects if p.name == "mnist1d-monitoring")

ws.add_run(project.id, report)
print("Report pushed to Evidently UI")
```

Refresh the Evidently UI at **{{< svcurl "evidently_port" >}}** → your project → you should see the new run with its drift scores.

## Simulate a monitoring schedule

In production you would push a report once per hour or once per day. Here is a minimal loop that simulates three consecutive batches with increasing noise:

```python
from evidently.ui.workspace import Workspace
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from mnist1d.data import make_dataset, get_dataset_args
import pandas as pd, time

cols = [f"t{i}" for i in range(40)]
args_ref = get_dataset_args()
d_ref = make_dataset(args_ref)
ref = pd.DataFrame(d_ref["x"], columns=cols)
ref["label"] = d_ref["y"]

ws = Workspace(url="{{< svcurl "evidently_port" >}}")
projects = ws.list_projects()
project = next(p for p in projects if p.name == "mnist1d-monitoring")

for noise, seed in [(0.2, 10), (0.4, 20), (0.6, 30)]:
    args = get_dataset_args()
    args.noise_scale = noise
    args.seed = seed
    d = make_dataset(args)
    cur = pd.DataFrame(d["x"], columns=cols)
    cur["label"] = d["y"]

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref, current_data=cur)
    ws.add_run(project.id, report)
    print(f"Pushed report: noise_scale={noise}")
    time.sleep(1)  # ensure distinct timestamps
```

After this loop, the project in the UI shows three runs with progressively higher drift scores.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Generate the reference and current datasets with different noise levels
- [ ] Run the drift report and open the HTML — identify which features drift most
- [ ] Push the report to the Evidently UI and confirm it appears
- [ ] Run the three-batch loop and watch drift scores increase in the UI
- [ ] Set `noise_scale=0.05` (very clean) and confirm the drift score drops to near zero
{{% /notice %}}
