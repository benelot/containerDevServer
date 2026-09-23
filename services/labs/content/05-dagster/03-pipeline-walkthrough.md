---
title: "Pipeline walkthrough"
weight: 3
---

## Asset 1 — `raw_dataset`

**What it does:** Downloads the MNIST 1D pickle from GitHub, or loads a local cache at `/tmp/mnist1d_data.pkl` if the file already exists.

```python
@dg.asset(group_name="data")
def raw_dataset(context: dg.AssetExecutionContext) -> dict:
    cache = "/tmp/mnist1d_data.pkl"
    if not os.path.exists(cache):
        urllib.request.urlretrieve(url, cache)
    with open(cache, "rb") as f:
        data = pickle.load(f)
    return {
        "X_train": np.array(data["x"],      dtype=np.float32),
        "y_train": np.array(data["y"],      dtype=np.int64),
        "X_test":  np.array(data["x_test"], dtype=np.float32),
        "y_test":  np.array(data["y_test"], dtype=np.int64),
    }
```

**Why the cache?** Network downloads inside a pipeline are a reliability risk. Once the file is on disk, reruns are instant and offline-safe.

**Output shape:** `X_train` is `(4000, 40)`, `X_test` is `(1000, 40)`, labels are integers 0–9.

---

## Asset 2 — `validated_dataset`

**What it does:** Converts the NumPy arrays to a Pandas DataFrame and runs a Pandera schema validation.

```python
@dg.asset(group_name="data")
def validated_dataset(context, raw_dataset: dict) -> dict:
    df = pd.DataFrame(X_train, columns=[f"t{i}" for i in range(40)])
    df["label"] = y_train
    schema = _build_schema(40)
    schema.validate(df)
    return raw_dataset
```

**The Pandera schema** checks every column:

```python
def _build_schema(n_features=40):
    cols = {f"t{i}": pa.Column(float, pa.Check.between(-8.0, 8.0))
            for i in range(n_features)}
    cols["label"] = pa.Column(int, pa.Check.isin(list(range(10))))
    return pa.DataFrameSchema(cols, coerce=True)
```

If any `t0`–`t39` value is outside `[-8.0, 8.0]`, or any label is not in `{0,...,9}`, Pandera raises a `SchemaError` and Dagster marks the asset as failed. The downstream assets (`data_quality_report`, `trained_model`) do not run.

**Why validate before training?** If your annotation pipeline produces out-of-range values — perhaps from a normalisation bug — you learn about it here, not after 30 epochs of training on garbage data.

---

## Asset 3 — `data_quality_report`

This asset runs two independent quality frameworks.

### Evidently

```python
report = Report(metrics=[DataQualityPreset(), DataDriftPreset()])
report.run(reference_data=ref, current_data=cur)
report.save_html("/tmp/evidently_report.html")
```

- **`DataQualityPreset`** checks for missing values, constant columns, and out-of-range values.
- **`DataDriftPreset`** runs a statistical test on each of the 40 features to detect whether the test-set distribution has shifted from the training-set distribution.

The reference data is the training set; current data is the test set. In production the current data would be live predictions collected since the last run.

### DeepChecks

```python
integrity_result = data_integrity().run(train_ds)
tt_result        = train_test_validation().run(train_ds, test_ds)
```

- **`data_integrity` suite** checks the training set in isolation: duplicate rows, rare categories, mixed data types, outliers.
- **`train_test_validation` suite** compares training and test sets: feature distribution similarity, label distribution similarity, train/test leakage.

Both suites export to HTML. All four files are logged to MLflow as artifacts under `mnist1d-quality / data-quality`.

The asset also logs four numeric metrics to MLflow: `integrity_passed`, `integrity_failed`, `traintest_passed`, `traintest_failed`. You can plot these over time to track whether data quality degrades across pipeline runs.

---

## Asset 4 — `trained_model`

### The network architecture

```
Input: (batch, 1, 40)           # one-channel 1D sequence
Conv1d(1 → 32, k=5)  + BN + ReLU + MaxPool(2)    # → (batch, 32, 20)
Conv1d(32 → 64, k=3) + BN + ReLU + MaxPool(2)    # → (batch, 64, 10)
Conv1d(64 → 128, k=3)+ BN + ReLU                 # → (batch, 128, 10)
AdaptiveAvgPool1d(1) + Flatten                    # → (batch, 128)
Linear(128 → 64) + ReLU + Dropout(0.3)
Linear(64 → 10)                                   # logits
```

**BatchNorm** after each Conv layer normalises activations within the batch, reducing sensitivity to initialisation and allowing higher learning rates.

**AdaptiveAvgPool1d(1)** collapses the time dimension regardless of input length, making the network robust to slight length variations.

**Dropout(0.3)** before the final linear layer reduces overfitting by randomly zeroing 30% of the hidden units during training.

### Training loop

```python
optimiser = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
criterion = nn.CrossEntropyLoss()

for epoch in range(1, 31):
    model.train()
    for xb, yb in train_ld:
        optimiser.zero_grad()
        criterion(model(xb), yb).backward()
        optimiser.step()
    if epoch % 5 == 0:
        # evaluate and log val_acc to MLflow
```

**Adam** with weight decay (`1e-4`) combines adaptive per-parameter learning rates with L2 regularisation.

**CrossEntropyLoss** applies log-softmax internally — the model outputs raw logits, not probabilities.

### MLflow logging

```python
with mlflow.start_run(run_name="dagster-conv1d") as run:
    mlflow.log_params({"epochs": 30, "batch_size": 128, "lr": 1e-3})
    # ... training loop logs val_acc every 5 epochs ...
    mlflow.pytorch.log_model(model, "model", registered_model_name="mnist1d-conv1d")
```

After the run, open MLflow at **{{< svcurl "mlflow_port" >}}** → experiment `mnist1d-dagster`. The run shows the parameter table and a val_acc curve. The model appears in **Models → mnist1d-conv1d** as a new version.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Open the Dagster asset graph and identify the four assets and their dependencies
- [ ] Trigger `mnist1d_full_pipeline` from the UI (click the job → **Materialise All**)
- [ ] Watch the run logs in real time — note which asset takes the longest
- [ ] Open MLflow and confirm the `mnist1d-quality` and `mnist1d-dagster` experiments have new runs
- [ ] Download the Evidently HTML report from MLflow and open it in your browser
- [ ] Check the MLflow Models page — confirm `mnist1d-conv1d` has a new version
{{% /notice %}}
