---
title: "Track the dataset"
weight: 3
---

## Generate and track MNIST 1D

First, generate the dataset and save it to disk:

```python
# Run in a Python shell or notebook
from mnist1d.data import make_dataset, get_dataset_args
import pickle, os

os.makedirs("data", exist_ok=True)
args = get_dataset_args()   # seed=42 by default
data = make_dataset(args)
with open("data/mnist1d_data.pkl", "wb") as f:
    pickle.dump(data, f)
print("Saved data/mnist1d_data.pkl")
```

Now track it with DVC:

```bash
dvc add data/mnist1d_data.pkl
```

DVC creates two files:
- `data/mnist1d_data.pkl.dvc` — the pointer file (commit this to Git)
- `data/.gitignore` — tells Git to ignore the actual data file

Add them both to Git:

```bash
git add data/mnist1d_data.pkl.dvc data/.gitignore
git commit -m "Track MNIST 1D dataset v1 (seed=42)"
```

## Push to the remote

```bash
dvc push
```

DVC uploads `data/mnist1d_data.pkl` to the MinIO bucket. You can verify the upload in the MinIO console at **{{< svcurl "dvc_minio_console_port" >}}** → bucket `dvc-cache`.

## Create a second version

Now generate a variant with different noise and track it as a second version:

```python
args2 = get_dataset_args()
args2.noise_scale = 0.3   # noisier than default 0.1
args2.seed = 99
data2 = make_dataset(args2)
with open("data/mnist1d_data.pkl", "wb") as f:
    pickle.dump(data2, f)
print("Saved noisier dataset")
```

```bash
dvc add data/mnist1d_data.pkl
git add data/mnist1d_data.pkl.dvc
git commit -m "Track MNIST 1D dataset v2 (noise_scale=0.3, seed=99)"
dvc push
```

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Generate the dataset and add it to DVC
- [ ] Confirm the `.dvc` pointer file was created and `data/mnist1d_data.pkl` is in `.gitignore`
- [ ] Push to the remote and verify the file appears in the MinIO console
- [ ] Create a second version with different generator args and push that too
- [ ] Run `git log --oneline` and confirm two commits exist with the dataset changes
{{% /notice %}}
