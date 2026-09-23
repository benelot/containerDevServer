---
title: "Troubleshooting"
weight: 4
---

## Common issues

### Prometheus target is `DOWN`

The target service is not running or the configured port is wrong. Check:

```bash
docker compose -f services/monitoring/docker-compose.yml logs prometheus | grep "error"
```

If the port changed (e.g. after `--random` port assignment), update `services/monitoring/prometheus/prometheus.yml` and reload Prometheus without restarting:

```bash
curl -X POST {{< svcurl "prometheus_port" >}}/-/reload
```

The `--web.enable-lifecycle` flag in `docker-compose.yml` enables this hot-reload.

### Grafana shows "No data" on all panels

The Prometheus datasource may not be connected. Go to **Configuration → Data sources → Prometheus** and click **Test**. If it fails, check that Prometheus is running:

```bash
curl {{< svcurl "prometheus_port" >}}/-/healthy
```

If Prometheus is healthy but Grafana cannot reach it, verify the datasource URL is `http://prometheus:9090` (internal Docker network), not `http://localhost:9090` (which resolves inside the Grafana container to itself).

### cAdvisor container exits with permission errors

On some Linux kernels, cAdvisor requires `--privileged` or specific capability flags. Check:

```bash
docker compose -f services/monitoring/docker-compose.yml logs cadvisor
```

If you see `permission denied` accessing `/sys/fs/cgroup`, add `privileged: true` to the cAdvisor service in `docker-compose.yml`.

### Imported dashboard shows "Plugin not installed"

Some community dashboards require the Grafana Pie Chart or Bar Chart plugins. Install them:

```bash
docker exec grafana grafana-cli plugins install grafana-piechart-panel
docker compose -f services/monitoring/docker-compose.yml restart grafana
```

### Disk usage is near 100%

Prometheus's time-series database grows over time. The default retention is 30 days (`PROMETHEUS_RETENTION=30d`). Reduce it in `services/monitoring/.env`:

```bash
PROMETHEUS_RETENTION=7d
```

Then restart Prometheus. Old data beyond the new retention window is purged automatically.
