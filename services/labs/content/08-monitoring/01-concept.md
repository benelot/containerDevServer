---
title: "Concept"
weight: 1
---

## The Prometheus pull model

Prometheus works by **scraping** — it sends an HTTP GET to a `/metrics` endpoint on each target every 15 seconds and stores the response. Targets are listed in `prometheus.yml`. You do not push metrics to Prometheus; Prometheus comes to you.

### Key terms

| Term | Meaning |
|---|---|
| **Scrape** | One HTTP GET to a `/metrics` endpoint |
| **Target** | A service Prometheus is configured to scrape |
| **Metric** | A named time series, e.g. `node_cpu_seconds_total` |
| **Label** | A key-value pair attached to a metric, e.g. `{instance="host:9100"}` |
| **PromQL** | Prometheus Query Language — used to select and aggregate metrics |
| **Exporter** | A sidecar process that translates a service's internal state to Prometheus format |

### Four exporters in this stack

**node\_exporter** — runs on the host (as a container with host PID namespace) and exposes:
- `node_cpu_seconds_total` — CPU time by mode (user, system, idle, iowait)
- `node_memory_MemAvailable_bytes` — free+reclaimable RAM
- `node_filesystem_avail_bytes` — disk free per mount point

**cAdvisor** — watches every Docker container and exposes:
- `container_cpu_usage_seconds_total` — per-container CPU
- `container_memory_usage_bytes` — per-container RSS memory
- `container_network_receive_bytes_total` — network in/out

**blackbox\_exporter** — probes HTTP endpoints and returns:
- `probe_success` — 1 if the endpoint returned 2xx, 0 otherwise
- `probe_duration_seconds` — round-trip time

**Prometheus itself** — exposes its own health via `prometheus_build_info` and `scrape_duration_seconds`.

### Grafana

Grafana queries Prometheus via PromQL and renders the results as panels in dashboards. It is configured with a Prometheus datasource automatically via the `provisioning` volume mount. The default home dashboard (`service_health.json`) shows a live health summary for all services.
