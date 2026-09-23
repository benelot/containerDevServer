---
title: "Setup"
weight: 2
---

## Start the service

```bash
./scripts/start.sh label-studio
```

Label Studio opens at **{{< svcurl "label_studio_port" >}}**.

Log in with:
- **Email:** `admin@example.com`
- **Password:** `changeme`

## Create a project

1. Click **Create Project**.
2. Name it `MNIST 1D Review`.
3. Skip the **Data Import** tab for now.
4. Open the **Labeling Setup** tab.

### Configure the label interface

Click **Custom template** and paste this XML:

```xml
<View>
  <Header value="Digit sequence — assign the correct class"/>
  <Text name="sequence_id" value="$id"/>
  <Text name="raw_values" value="$values_preview"/>
  <Choices name="digit" toName="raw_values" choice="single" required="true">
    <Choice value="0"/><Choice value="1"/><Choice value="2"/>
    <Choice value="3"/><Choice value="4"/><Choice value="5"/>
    <Choice value="6"/><Choice value="7"/><Choice value="8"/>
    <Choice value="9"/>
  </Choices>
</View>
```

Click **Save**.

## Prepare samples for import

Run this in a Python shell or JupyterLab notebook:

```python
import json, pickle
import numpy as np

with open("data/mnist1d_data.pkl", "rb") as f:
    d = pickle.load(f)

tasks = []
for i in range(20):  # annotate 20 samples
    x = d["x"][i].tolist()
    y = int(d["y"][i])
    tasks.append({
        "data": {
            "id": f"sample_{i:04d}",
            "values_preview": f"Class hint: {y} | First 8 values: {[round(v, 3) for v in x[:8]]}",
            "true_label": y   # hidden ground truth — useful for inter-annotator agreement
        }
    })

with open("data/label_studio_tasks.json", "w") as f:
    json.dump(tasks, f, indent=2)

print(f"Wrote {len(tasks)} tasks to data/label_studio_tasks.json")
```

## Import tasks

1. In your project, click **Import**.
2. Upload `data/label_studio_tasks.json`.
3. Label Studio shows 20 tasks ready to annotate.

{{% expand title="Start here if you skipped earlier labs" %}}
You only need Label Studio running. The dataset is generated here, not read from a previous lab.
```bash
pip install mnist1d
./scripts/start.sh label-studio
./scripts/start.sh dvc
```
Then generate the tasks as shown above (the `make_dataset` call replaces reading from `data/mnist1d_data.pkl`):
```python
from mnist1d.data import make_dataset, get_dataset_args
import json
args = get_dataset_args()
d = make_dataset(args)
# continue with the tasks loop above
```
{{% /expand %}}
