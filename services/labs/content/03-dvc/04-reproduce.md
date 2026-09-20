---
title: "Reproduce a version"
weight: 4
---

## Restore an earlier dataset version

With two versions tracked, you can switch between them using standard Git commands. DVC handles the data download automatically.

### Delete the current data file

```bash
rm data/mnist1d_data.pkl
```

### Check out version 1

```bash
git checkout HEAD~1 -- data/mnist1d_data.pkl.dvc
dvc pull
```

The `.dvc` file now points to the v1 hash. DVC downloads that exact file from MinIO.

Verify:

```python
import pickle
with open("data/mnist1d_data.pkl", "rb") as f:
    d = pickle.load(f)
print("noise_scale was:", 0.1)   # v1 used defaults
print("Shape:", d['x'].shape)
```

### Restore to the latest version

```bash
git checkout HEAD -- data/mnist1d_data.pkl.dvc
dvc pull
```

## Why this matters for ML

This is the reproducibility guarantee that makes CRISP-DM feedback loops safe. When Evidently detects drift and Label Studio produces new annotations, the new dataset is a separate DVC version. The old training run is still linked to the old pointer. If you need to understand what changed between the two model versions, `git diff` on the `.dvc` file shows exactly which dataset hash changed.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Delete `data/mnist1d_data.pkl` and confirm it is gone
- [ ] Restore v1 with `git checkout HEAD~1` + `dvc pull` and verify the file is back
- [ ] Restore the latest version and confirm the noise level is different
- [ ] Run `dvc status` to confirm there are no uncommitted data changes
{{% /notice %}}

## Useful DVC commands

```bash
dvc status          # show which tracked files have changed
dvc diff            # compare current data to last commit
dvc fetch           # download data without switching the working copy
dvc gc -c           # remove cached data not referenced by any commit
```
