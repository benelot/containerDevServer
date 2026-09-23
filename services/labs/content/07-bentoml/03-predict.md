---
title: "Predict"
weight: 3
---

## Send a single sequence

```bash
curl -X POST {{< svcurl "bentoml_port" >}}/predict \
  -H "Content-Type: application/json" \
  -d '{"sequences": [[0.1, 0.2, -0.1, 0.3, 0.0, 0.1, 0.2, -0.2,
                       0.1, 0.0, 0.2, 0.3, -0.1, 0.2, 0.1, 0.0,
                       0.3, 0.2, 0.1, -0.1, 0.0, 0.2, 0.3, 0.1,
                       0.2, 0.0, -0.2, 0.1, 0.3, 0.2, 0.1, 0.0,
                       0.2, 0.3, -0.1, 0.1, 0.0, 0.2, 0.1, 0.3]]}'
```

Expected response:

```json
{
  "predictions": [7],
  "probabilities": [[0.01, 0.02, 0.03, 0.05, 0.02, 0.04, 0.03, 0.72, 0.05, 0.03]]
}
```

## Send real MNIST 1D samples from Python

```python
import requests, pickle, json
import numpy as np

with open("data/mnist1d_data.pkl", "rb") as f:
    d = pickle.load(f)

# Send 5 test samples
X = d["x_test"][:5].tolist()
y_true = d["y_test"][:5].tolist()

resp = requests.post(
    "{{< svcurl "bentoml_port" >}}/predict",
    json={"sequences": X}
)
resp.raise_for_status()
result = resp.json()

print("True labels: ", y_true)
print("Predictions: ", result["predictions"])

# Show confidence for each prediction
for i, (pred, probs) in enumerate(zip(result["predictions"], result["probabilities"])):
    confidence = max(probs)
    correct = "✓" if pred == y_true[i] else "✗"
    print(f"  Sample {i}: pred={pred}, true={y_true[i]} {correct}  confidence={confidence:.1%}")
```

## Generate new sequences with the MNIST 1D generator

The generator creates sequences you can immediately send to the model — no saved dataset required:

```python
import requests
from mnist1d.data import make_dataset, get_dataset_args

args = get_dataset_args()
args.noise_scale = 0.3   # try different noise levels
args.seed = 42
d = make_dataset(args)

samples = d["x"][:10].tolist()
labels  = d["y"][:10].tolist()

resp = requests.post(
    "{{< svcurl "bentoml_port" >}}/predict",
    json={"sequences": samples}
)
preds = resp.json()["predictions"]

correct = sum(p == t for p, t in zip(preds, labels))
print(f"Accuracy on 10 generated samples: {correct}/10")
print(f"Predictions: {preds}")
print(f"True labels: {labels}")
```

Try `noise_scale=0.0`, `0.3`, and `0.8` to see how accuracy drops as the sequences become noisier.

## Collect predictions for drift monitoring

In a real deployment you would log each request for later comparison with the training distribution. A minimal collector:

```python
import csv, time, requests
from mnist1d.data import make_dataset, get_dataset_args

log_file = "data/prediction_log.csv"

with open(log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "true_label", "pred_label", "confidence"])

for noise in [0.1, 0.2, 0.3, 0.4]:
    args = get_dataset_args()
    args.noise_scale = noise
    d = make_dataset(args)
    for i in range(10):
        seq = d["x"][i:i+1].tolist()
        true = int(d["y"][i])
        resp = requests.post("{{< svcurl "bentoml_port" >}}/predict",
                             json={"sequences": seq})
        result = resp.json()
        pred = result["predictions"][0]
        conf = max(result["probabilities"][0])
        with open(log_file, "a", newline="") as f:
            csv.writer(f).writerow([time.time(), true, pred, f"{conf:.4f}"])

print("Logged 40 predictions to", log_file)
```

This CSV becomes the "current data" for the Evidently drift report in Lab 6.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Send a `curl` request to `/predict` and read the response
- [ ] Send 5 real MNIST 1D test samples and calculate the accuracy
- [ ] Use the generator to create sequences with `noise_scale=0.8` — does accuracy drop?
- [ ] Collect 40 predictions into a CSV and inspect it
- [ ] Call `/health` and confirm it reports `"status": "ok"`
{{% /notice %}}
