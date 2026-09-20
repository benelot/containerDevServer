# Monitoring

## What it does

This stack provides observability at two levels:

- **Service health** -- an HTTP probe hits every service every 15 seconds and records whether it responded with 2xx. The Grafana home dashboard shows a live UP/DOWN tile for each service plus response time trends.
- **Hardware metrics** -- CPU, RAM, disk I/O, and network are collected from the host. Per-container CPU and RAM show which service is consuming resources. Optional GPU metrics are collected when the NVIDIA Container Toolkit is present.

## Components

| Container | Image | Role |
|---|---|---|
| `prometheus` | `prom/prometheus` | Time-series database; scrapes all exporters |
| `grafana` | `grafana/grafana` | Dashboard UI; provisioned automatically |
| `node_exporter` | `prom/node-exporter` | Host CPU, RAM, disk, network |
| `cadvisor` | `gcr.io/cadvisor/cadvisor` | Per-container CPU and RAM |
| `blackbox_exporter` | `prom/blackbox-exporter` | HTTP probes for all service endpoints |
| `dcgm_exporter` | `nvcr.io/nvidia/k8s/dcgm-exporter` | NVIDIA GPU metrics (opt-in, see below) |

## Default ports

| Service | Port | Variable |
|---|---|---|
| Prometheus | 9090 | `PROMETHEUS_PORT` |
| Grafana | 3002 | `GRAFANA_PORT` |
| cAdvisor | 8082 | `CADVISOR_PORT` |

## Quick start

```bash
./scripts/start.sh monitoring
# Grafana: http://localhost:3002  (admin / admin -- change in .env)
# Prometheus: http://localhost:9090
```

The Grafana home dashboard loads automatically with:
- Service health tiles (UP/DOWN per service)
- Response time history
- Host CPU, RAM, Disk I/O
- Per-container CPU and RAM

## GPU monitoring

GPU metrics require the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html). Start with the `gpu` profile to include `dcgm_exporter`:

```bash
docker compose -f services/monitoring/docker-compose.yml --profile gpu up -d
```

On hosts without NVIDIA hardware, omit `--profile gpu` and the GPU rows in the dashboard stay empty.

## Community dashboards

Import these from grafana.com for deeper metrics (Grafana > Dashboards > Import):

| Dashboard | ID | Use |
|---|---|---|
| Node Exporter Full | `1860` | Detailed host CPU, RAM, network, disk |
| Docker + cAdvisor | `14282` | Per-container resource usage with history |
| DCGM GPU Metrics | `12239` | NVIDIA GPU utilisation, memory, temperature |

## Data retention

Prometheus defaults to 30 days. Change `PROMETHEUS_RETENTION` in `.env` (e.g. `90d`, `10GB`). Grafana dashboards and alert rules persist in the `grafana_data` named volume.

## CRISP-DM role

Monitoring is infrastructure that supports every phase, but it is most critical during **Deployment**.

| Phase | What monitoring provides |
|---|---|
| Modelling | cAdvisor shows which training container is saturating CPU/GPU so you know when to move to HPC |
| Evaluation | Response time on BentoML `/predict` shows inference latency as a quality metric |
| Deployment | Service health tiles give an instant view of which services are up before running a pipeline |
| Deployment | Hardware trends reveal memory pressure or disk exhaustion before they cause pipeline failures |
