---
title: "Lab 8 — Monitoring"
weight: 8
---

## Infrastructure visibility

You have eight services running. Without visibility into their resource usage you cannot tell whether a slow Dagster run is caused by a CPU spike, a memory limit, or a network issue. Prometheus and Grafana give you that visibility.

In this lab you will:

1. Start the monitoring stack and explore the pre-built dashboards
2. Understand what Prometheus collects and how Grafana displays it
3. Import community dashboards and navigate the service-health overview

### Services used in this lab

| Service | Purpose |
|---|---|
| Prometheus | Scrape metrics from all services every 15 seconds |
| Grafana | Visualise scraped metrics; alerting |
| node\_exporter | Host-level CPU, RAM, disk, network |
| cAdvisor | Per-container CPU, RAM, network |

```bash
./scripts/start.sh monitoring
```

### CRISP-DM connection

Monitoring covers the **Deployment** phase. Infrastructure health directly affects model serving reliability — a container that is OOM-killed or disk-full will silently fail predictions.
