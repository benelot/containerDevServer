# Monitoring

Prometheus + Grafana stack for hardware metrics and service health monitoring.

## CRISP-DM role

| Phase | Contribution |
|---|---|
| Deployment | Track service uptime, response latency, and hardware utilisation over time |

Monitoring closes the operational side of the CRISP-DM loop: it surfaces infrastructure problems (a service going down, a GPU running out of memory, a container consuming excessive CPU) before they affect experiments or model serving.

## Components

| Container | Port | Purpose |
|---|---|---|
| `grafana` | 3002 | Dashboards and alerting UI |
| `prometheus` | 9090 | Metrics collection and storage |
| `node_exporter` | 9100 | Host CPU, RAM, disk, network |
| `cadvisor` | 8082 | Per-container CPU and RAM |
| `blackbox_exporter` | 9115 | HTTP health probes for all services |
| `dcgm_exporter` | 9400 | NVIDIA GPU metrics (opt-in, `--profile gpu`) |

## Dashboards

**Service Health** — UP/DOWN status for every service in the stack (JupyterLab, MLflow, Dagster, Evidently, BentoML, Label Studio), HTTP response time history, and probe success rate.

**Hardware** — Host CPU usage, memory usage, disk I/O, and network throughput from node_exporter.

**Containers** — Per-container CPU and memory from cAdvisor.

**GPU** (when enabled) — GPU utilisation, memory usage, and temperature from dcgm_exporter.

## Quickstart

```bash
./scripts/start.sh monitoring
# http://localhost:3002  — Grafana  (admin / admin on first login)
# http://localhost:9090  — Prometheus
```

## GPU metrics

GPU monitoring uses the NVIDIA DCGM exporter and requires the NVIDIA Container Toolkit on the host. It is gated behind a Docker Compose profile so non-NVIDIA hosts start the stack without errors.

```bash
# Start with GPU metrics enabled (NVIDIA host only)
cd services/monitoring
docker compose --profile gpu up -d
```

## Adding a new service to health monitoring

Add a target to `prometheus/prometheus.yml` under the `blackbox` job:

```yaml
- targets:
  - http://host.docker.internal:<port>
```

Prometheus will begin probing the endpoint immediately; it appears on the Service Health dashboard within one scrape interval (15 seconds by default).

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GRAFANA_PORT` | `3002` | Grafana UI port |
| `PROMETHEUS_PORT` | `9090` | Prometheus port |
| `CADVISOR_PORT` | `8082` | cAdvisor port |
| `GF_SECURITY_ADMIN_PASSWORD` | `admin` | Grafana admin password — change before production use |
