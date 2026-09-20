---
title: "Summary"
weight: 5
---

## What you did

- Started the monitoring stack (Prometheus, Grafana, node\_exporter, cAdvisor, blackbox\_exporter)
- Verified all scrape targets are `UP` in Prometheus
- Imported three community dashboards: Node Exporter Full, cAdvisor, Blackbox Exporter
- Wrote PromQL queries to inspect CPU, RAM, and probe success metrics
- Watched container resource usage change during a live Dagster pipeline run

## CRISP-DM phases covered

| Phase | How monitoring contributes |
|---|---|
| Deployment | Infrastructure health is observable — failures are detected in seconds, not hours |
| Evaluation | Resource usage during training runs informs hardware sizing decisions |

## The complete stack

You have now used all eight services:

| Lab | Service | CRISP-DM phase |
|---|---|---|
| 1 | MLflow | Modelling, Evaluation |
| 2 | JupyterLab | Data Understanding, Modelling |
| 3 | DVC | Data Preparation |
| 4 | Label Studio | Data Understanding, Data Preparation |
| 5 | Dagster | Data Preparation, Modelling, Evaluation |
| 6 | Evidently | Deployment |
| 7 | BentoML | Deployment |
| 8 | Monitoring | Deployment |

The CRISP-DM loop is complete. Evidently detects drift → Label Studio collects new labels → DVC versions the data → Dagster retrains → MLflow registers → BentoML serves → repeat.

## Start everything at once

```bash
for svc in mlflow dvc label-studio jupyterlab dagster evidently bentoml monitoring; do
    ./scripts/start.sh "$svc"
done
```

Then open the labs at **{{< svcurl "labs_port" >}}** to follow along.
