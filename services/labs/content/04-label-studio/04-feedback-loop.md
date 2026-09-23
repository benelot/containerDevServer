---
title: "Feedback loop"
weight: 4
---

## Track the annotated batch with DVC

The annotated batch is new data — it should become a versioned DVC artifact, not an uncommitted local file.

```bash
dvc add data/annotated_batch_v1.pkl
git add data/annotated_batch_v1.pkl.dvc data/.gitignore
git commit -m "Add annotated batch v1 — 20 human-labeled MNIST 1D samples"
dvc push
```

The `.dvc` pointer file records the exact hash of this annotation batch. Every future model trained on it will reference this commit.

## How Dagster picks up new data

The Dagster pipeline reads from a path you configure. When you point it at `data/annotated_batch_v1.pkl` and trigger a new run, the pipeline:

1. **Validates** the new batch with Pandera (schema check — correct shape and label range)
2. **Runs DeepChecks** to compare the new batch against the original training data (distribution shift check)
3. **Retrains** the Conv1D model with the combined dataset
4. **Logs** the new run to MLflow and registers a new model version

The Git commit hash of the `.dvc` pointer is what links an MLflow run to its exact training data. This is the traceability chain that CRISP-DM requires.

## The full loop visualised

```
Label Studio export
        │
        ▼
  dvc add + git commit  ──► Git hash H2
        │
        ▼
  Dagster run  ──► MLflow run (params + metrics + artifact)
        │                      │
        │                      └── linked to Git hash H2
        ▼
  MLflow registry: "mnist1d-conv1d" Staging → Production
        │
        ▼
  BentoML reloads model on next request
        │
        ▼
  Evidently monitors new predictions
        │
        ▼
  Drift detected? → new Label Studio project
```

Each arrow is traceable. You can walk the chain backward from any production model to the exact annotations that produced it.

## Simulate the next iteration

To see the loop in action without a full Dagster run, generate a second annotation batch with slightly different noise and push it:

```python
from mnist1d.data import make_dataset, get_dataset_args
import pickle, numpy as np

args = get_dataset_args()
args.noise_scale = 0.2   # slightly more noise than v1 default
args.seed = 77
d2 = make_dataset(args)

batch2 = {"x": d2["x"][:20], "y": d2["y"][:20]}
with open("data/annotated_batch_v2.pkl", "wb") as f:
    pickle.dump(batch2, f)
```

```bash
dvc add data/annotated_batch_v2.pkl
git add data/annotated_batch_v2.pkl.dvc
git commit -m "Add annotated batch v2 — 20 samples, noise_scale=0.2"
dvc push
```

Now you have two distinct data versions. `git log --oneline data/annotated_batch_v*.dvc` shows their history.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Track `annotated_batch_v1.pkl` with DVC and push
- [ ] Confirm the `.dvc` file was committed and the file appears in MinIO
- [ ] Generate and push `annotated_batch_v2.pkl` as a second batch
- [ ] Run `git log --oneline` and confirm both annotation commits exist
- [ ] Use `git checkout HEAD~1 -- data/annotated_batch_v1.pkl.dvc && dvc pull` to restore v1
{{% /notice %}}
