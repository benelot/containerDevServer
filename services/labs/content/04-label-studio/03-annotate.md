---
title: "Annotate"
weight: 3
---

## Annotate the tasks

Click **Label All Tasks** in your project.

Label Studio shows the sequence description and a ten-button choice panel. For each task:

1. Read the values preview.
2. Click the digit you believe is correct.
3. Click **Submit** (or press `W` to submit and advance).

The progress counter in the top bar updates after each submission. Annotate all 20 tasks.

## Review completed annotations

After finishing, go to the project home and click the **Completed** tab. You can see each task's annotation and the user who submitted it.

To inspect a specific task, click it and then **Edit** to change the label if needed. Label Studio stores full annotation history so corrections are always traceable.

## Export the annotations

Click **Export** → choose **JSON** → **Export**.

The downloaded file contains every task with its annotation. Save it to your working directory:

```bash
mv ~/Downloads/project-*.json data/annotations_v1.json
```

Inspect the structure:

```python
import json

with open("data/annotations_v1.json") as f:
    data = json.load(f)

for task in data[:3]:
    sid  = task["data"]["id"]
    hint = task["data"]["values_preview"]
    chosen = task["annotations"][0]["result"][0]["value"]["choices"][0]
    print(f"{sid}  hint={hint[:30]}  annotated={chosen}")
```

Each `result[0]["value"]["choices"][0]` is the string the annotator clicked — e.g. `"3"`.

## Convert to a training-ready format

The raw Label Studio JSON needs a small conversion before DVC tracks it:

```python
import json, pickle
import numpy as np

with open("data/annotations_v1.json") as f:
    ls_data = json.load(f)

# rebuild index from original dataset
with open("data/mnist1d_data.pkl", "rb") as f:
    original = pickle.load(f)

annotated_x, annotated_y = [], []
for task in ls_data:
    idx = int(task["data"]["id"].split("_")[1])
    chosen_label = int(task["annotations"][0]["result"][0]["value"]["choices"][0])
    annotated_x.append(original["x"][idx].tolist())
    annotated_y.append(chosen_label)

export = {"x": np.array(annotated_x), "y": np.array(annotated_y)}

with open("data/annotated_batch_v1.pkl", "wb") as f:
    pickle.dump(export, f)

print(f"Exported {len(annotated_y)} samples with human labels")
```

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Create the project with the XML label config
- [ ] Import the 20 tasks and annotate all of them
- [ ] Export the JSON and inspect its structure in Python
- [ ] Run the conversion script and confirm `data/annotated_batch_v1.pkl` exists
- [ ] Check the agreement rate: how many of your labels match the original `true_label` field?
{{% /notice %}}
