---
title: "Run and inspect"
weight: 4
---

## Trigger the pipeline

In the Dagster UI at **{{< svcurl "dagster_port" >}}**:

1. Click **Jobs** in the left sidebar.
2. Click `mnist1d_full_pipeline`.
3. Click **Materialise All** in the top right.
4. Click **Launch Run**.

The run opens and shows a live asset graph. Completed assets turn green; failed ones turn red.

## Read the run logs

Click any asset in the running graph to open its log panel. Useful lines to find:

| Asset | Log line to look for |
|---|---|
| `raw_dataset` | `Train: (4000, 40)  Test: (1000, 40)` |
| `validated_dataset` | `Pandera validation passed — 4,000 rows × 40 features` |
| `data_quality_report` | `DeepChecks — integrity: N passed / M failed` |
| `trained_model` | `Epoch 30  val_acc=0.9XX` |

## Inspect MLflow results

Open **{{< svcurl "mlflow_port" >}}**.

### Quality run

- Experiment: `mnist1d-quality`
- Run: `data-quality`
- Artifacts: `evidently/evidently_report.html`, `deepchecks/deepchecks_integrity.html`, `deepchecks/deepchecks_train_test.html`

Click the Evidently artifact and open the HTML. The **Data Drift** section shows a drift score per feature; values near 0 mean the test set is statistically similar to training.

### Training run

- Experiment: `mnist1d-dagster`
- Run: `dagster-conv1d`
- Params: `epochs`, `batch_size`, `lr`, `source`
- Metrics chart: `val_acc` — should reach above 90% by epoch 30

### Registered model

- **Models → mnist1d-conv1d**
- The new version is listed with a link back to the run that created it
- To promote to Production (so BentoML picks it up): click the version → **Stage → Production**

## Re-run to see iteration in action

Edit one hyperparameter in the pipeline file and re-trigger:

```bash
# In services/dagster/pipelines/mnist1d_pipeline.py
# Change:   mlflow.log_params({"epochs": 30, "lr": 1e-3, ...})
# To:       mlflow.log_params({"epochs": 40, "lr": 5e-4, ...})
# And update the range(1, 31) → range(1, 41)
```

After the second run you will see two runs in the `mnist1d-dagster` experiment. Use MLflow's **Compare** feature to put the val_acc curves side by side.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Trigger a full pipeline run and confirm all four assets turn green
- [ ] Read the Evidently HTML report — which features show the most drift?
- [ ] Open DeepChecks train-test HTML — does any check fail?
- [ ] Promote the trained model to Production in the MLflow registry
- [ ] (Optional) Change `epochs` or `lr`, re-run, and compare the two runs in MLflow
{{% /notice %}}
