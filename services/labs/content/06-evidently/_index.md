---
title: "Lab 6 — Evidently"
weight: 6
---

## Monitoring closes the deployment loop

A model deployed to production degrades over time as the real-world data distribution shifts away from the training distribution. Evidently measures that shift continuously and makes it visible.

In this lab you will:

1. Start the Evidently UI and create a monitoring project
2. Generate drift reports from MNIST 1D data simulating production shift
3. Read the reports in the UI and understand when to trigger retraining

### Services used in this lab

| Service | Purpose |
|---|---|
| Evidently UI | Persistent project workspace with report history |

```bash
./scripts/start.sh evidently
```

### CRISP-DM connection

Evidently covers the **Deployment** and feedback-into-**Business Understanding** phases. When Evidently reports drift beyond a threshold, it is the signal that CRISP-DM's iteration loop should begin again with new data collection and labeling.
