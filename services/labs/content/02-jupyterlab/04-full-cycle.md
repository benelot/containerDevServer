---
title: "Run the full notebook"
weight: 4
---

## The CRISP-DM notebook

The repo includes a complete CRISP-DM example notebook at `notebooks/mnist1d_crisp_dm.ipynb`. It walks through all six phases on the MNIST 1D dataset:

| Section | CRISP-DM phase | What it does |
|---|---|---|
| Dataset exploration | Data Understanding | Plots samples, checks class balance, inspects feature statistics |
| Schema validation | Data Preparation | Runs Pandera to validate feature ranges and label domain |
| Training | Modelling | Trains a Conv1D with BatchNorm; logs every epoch to MLflow |
| Evaluation | Evaluation | Confusion matrix, per-class accuracy, t-SNE projection |
| Registration | Deployment | Registers the best model in MLflow Model Registry |

## Running it

1. In the JupyterLab file browser, open `notebooks/mnist1d_crisp_dm.ipynb`.
2. Click **Kernel → Restart Kernel and Run All Cells**.
3. Watch the output. The training section takes about 60 seconds on CPU.

After the run completes, open **{{< svcurl "mlflow_port" >}}** and find the `mnist1d` experiment. A new run named `conv1d-mnist1d` will appear with 30 logged metric steps.

## What the notebook logs to MLflow

| Logged item | Type | Description |
|---|---|---|
| `epochs`, `lr`, `batch_size`, `optimizer` | Parameters | Training configuration |
| `val_acc` | Metric (per epoch) | Validation accuracy at each epoch |
| Confusion matrix PNG | Artifact | Class-level prediction heatmap |
| t-SNE plot PNG | Artifact | 2D projection of learned embeddings |
| `model/` | Artifact | Registered PyTorch model |

## The t-SNE section

Near the end of the notebook, a t-SNE projection shows how well the model separates classes in embedding space. Each point is a test sample coloured by true class. Well-separated clusters mean the model has learned useful representations. If clusters overlap, the model is confused between those digit classes.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Run the notebook end to end without errors
- [ ] Open the MLflow run and confirm 30 `val_acc` data points were logged
- [ ] Download the confusion matrix artifact and identify which two digit classes the model most often confuses
- [ ] Change the `lr` parameter in the training cell to `5e-4`, re-run training only, and compare the two runs in MLflow
{{% /notice %}}

{{% notice style="tip" %}}
You can re-run just the training section by clicking the first training cell and pressing **Shift+Enter** on each cell in sequence. You do not need to re-run the data loading cells.
{{% /notice %}}
