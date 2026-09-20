---
title: "Lab 3 — DVC"
chapter: true
weight: 4
pre: "<b>Lab 3. </b>"
---

# Lab 3 — DVC

**Dataset versioning and reproducibility.**

Code is versioned with Git. Data is not — unless you use a tool like DVC. Without it, the same training script produces different results depending on which version of the data happens to be on disk.

By the end of this lab you will have:
- A DVC remote backed by a local MinIO instance
- The MNIST 1D dataset tracked and pushed to the remote
- Experience reproducing an earlier dataset version from a Git commit

**Services needed for this lab:** DVC (MinIO remote only).

```bash
./scripts/start.sh dvc
```
