---
title: "Dashboards"
weight: 3
---

## Import community dashboards

Grafana has a library of community-maintained dashboards that work with standard exporters. Import three:

### Node Exporter Full (ID 1860)

Shows host CPU, RAM, disk I/O, and network in one scrollable dashboard.

1. In Grafana: **Dashboards → Import**.
2. Enter `1860` → **Load** → select your Prometheus datasource → **Import**.

Key panels to read:
- **CPU Busy** — percentage of time not idle; should be below 80% under load
- **RAM Used** — physical memory in use; watch this during Dagster training runs
- **Disk Space Used** — if this approaches 100%, DVC push and Docker pulls will fail

### cAdvisor (ID 14282)

Shows per-container resource usage.

Import with ID `14282`. After import, select a container from the **container** dropdown at the top. During a Dagster pipeline run, select the Dagster container and watch CPU and memory rise during the Conv1D training asset.

### Blackbox Exporter (ID 12239)

Shows HTTP probe results: response time and success rate per endpoint.

Import with ID `12239`. This dashboard shows whether each service's health endpoint is responding and how long it takes.

## Write a PromQL query

Open **{{< svcurl "prometheus_port" >}}/graph** and try these queries:

```promql
# Host CPU usage (all cores, averaged)
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)

# Available RAM in GiB
node_memory_MemAvailable_bytes / 1024^3

# Total container memory used
sum(container_memory_usage_bytes{name!=""})

# HTTP probe success (1=up, 0=down) per job
probe_success
```

Click the **Graph** tab to see each metric as a time series.

## Watch a pipeline run

While a Dagster pipeline is running (Lab 5), switch to the cAdvisor dashboard and select the `dagster-webserver` container. The training asset will cause a visible CPU spike lasting 1–2 minutes. Memory rises gradually as the model and batch tensors are loaded.

This is the practical use of monitoring: if training is consistently near 100% CPU, the host machine needs more cores or the batch size should be reduced.

{{% notice style="green" title="Exercise" icon="check-circle" %}}
- [ ] Open `/targets` in Prometheus and confirm all targets are `UP`
- [ ] Import dashboards 1860, 14282, and 12239 in Grafana
- [ ] Write a PromQL query for available RAM and note the current value
- [ ] Trigger a Dagster pipeline run and watch the CPU panel in the cAdvisor dashboard
- [ ] Find which container is using the most memory right now
{{% /notice %}}
