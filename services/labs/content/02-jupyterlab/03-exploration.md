---
title: "Explore the data"
weight: 3
---

## Generate and inspect MNIST 1D

Open a new notebook and run the following cells one at a time, reading the output before moving to the next.

### Generate the dataset

```python
from mnist1d.data import make_dataset, get_dataset_args
import numpy as np

args = get_dataset_args()
data = make_dataset(args)

print("Train sequences:", data['x'].shape)      # (4000, 40)
print("Train labels:   ", data['y'].shape)       # (4000,)
print("Test sequences: ", data['x_test'].shape)  # (1000, 40)
print("Classes:        ", np.unique(data['y']))  # 0..9
```

### Plot one sample per class

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 5, figsize=(14, 4))
for digit in range(10):
    idx = np.where(data['y'] == digit)[0][0]   # first sample of this class
    ax  = axes[digit // 5][digit % 5]
    ax.plot(data['x'][idx], lw=1.5)
    ax.set_title(f"Digit {digit}")
    ax.set_ylim(-3, 3)
    ax.tick_params(labelsize=7)
plt.suptitle("One sample per digit class", y=1.02)
plt.tight_layout()
plt.show()
```

Each sequence looks like a deformed sine wave. The digit class determines the underlying template; `noise_scale` and `padding` control how much variation is added.

### Compare different generator settings

The generator's arguments let you control the dataset's difficulty:

```python
# Noisier dataset — harder for the model
noisy_args = get_dataset_args()
noisy_args.noise_scale = 0.5   # default is 0.1
noisy_data = make_dataset(noisy_args)

# Plot one class from both datasets side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3))
ax1.plot(data['x'][0],       lw=1.5); ax1.set_title("Default noise")
ax2.plot(noisy_data['x'][0], lw=1.5); ax2.set_title("5× noise")
plt.tight_layout(); plt.show()
```

{{% notice style="info" %}}
This noise-scaling capability is used in the Evidently lab (Lab 6) to simulate data drift: the production dataset is generated with higher noise, and Evidently detects that the distribution has shifted from the training data.
{{% /notice %}}

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Generate the dataset and print its shapes
- [ ] Plot one sample per class — can you see patterns between digits?
- [ ] Generate a second dataset with `noise_scale=0.3` and plot class 0 from both side by side
- [ ] Count how many samples per class exist in the training set — is it balanced?
{{% /notice %}}

### Count samples per class

```python
import pandas as pd
counts = pd.Series(data['y']).value_counts().sort_index()
print(counts)
counts.plot(kind='bar', title='Samples per class', xlabel='Digit', ylabel='Count')
plt.tight_layout(); plt.show()
```

MNIST 1D is balanced by design — 400 samples per class. Real-world datasets are rarely this convenient.
