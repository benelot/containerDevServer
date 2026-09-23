---
title: "Setup"
weight: 2
---

## Start the monitoring stack

```bash
./scripts/start.sh monitoring
```

This starts Prometheus, Grafana, node\_exporter, cAdvisor, and blackbox\_exporter.

Verify each service:

```bash
# Prometheus — should return {"status":"success"}
curl {{< svcurl "prometheus_port" >}}/-/healthy

# Grafana — should return 200
curl -s -o /dev/null -w "%{http_code}" {{< svcurl "grafana_port" >}}/api/health

# cAdvisor — should return an HTML page
curl -s -o /dev/null -w "%{http_code}" {{< svcurl "cadvisor_port" >}}
```

## Open Grafana

Navigate to **{{< svcurl "grafana_port" >}}**.

Log in with:
- **Username:** `admin`
- **Password:** `admin`

The home dashboard (`service_health.json`) opens automatically and shows:
- HTTP probe status for all configured services
- cAdvisor container memory usage
- Node memory and CPU panels

## Explore Prometheus targets

Open **{{< svcurl "prometheus_port" >}}/targets**.

Each row shows a scrape target with its last scrape time and status. Healthy targets show `UP` in green. If any target shows `DOWN`, the service is not running or the configured port is wrong.

The targets are defined in `services/monitoring/prometheus/prometheus.yml`:

```yaml
- job_name: 'node-exporter'
  static_configs:
    - targets: ['node_exporter:9100']
- job_name: 'cadvisor'
  static_configs:
    - targets: ['cadvisor:8080']
```

{{% expand title="Start here if you skipped earlier labs" %}}
Only the monitoring stack is needed for this lab.
```bash
./scripts/start.sh monitoring
```
{{% /expand %}}
