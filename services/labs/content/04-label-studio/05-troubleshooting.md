---
title: "Troubleshooting"
weight: 5
---

## Common issues

### Cannot log in — "Invalid credentials"

The default credentials are `admin@example.com` / `changeme`. If you changed them via environment variables, check `services/label-studio/.env`:

```bash
grep LABEL_STUDIO services/label-studio/.env
```

If you forgot the password, reset the container volume and restart:

```bash
docker compose -f services/label-studio/docker-compose.yml down -v
./scripts/start.sh label-studio
```

This wipes all projects and annotations. Export first if any data matters.

### Import fails — "Unsupported file format"

Label Studio JSON import expects an array of task objects, each with a `data` key. A common mistake is uploading the raw Python dict instead of the list. Verify:

```python
import json
with open("data/label_studio_tasks.json") as f:
    t = json.load(f)
print(type(t), len(t))   # should be <class 'list'> 20
print(t[0].keys())        # should contain 'data'
```

### Export download is empty

Label Studio only includes tasks that have at least one annotation. If you exported before finishing all tasks, the JSON will contain only the completed ones. Annotate the remaining tasks and export again.

### Label Studio is slow or unresponsive

The container shares the host's resources. If JupyterLab and MLflow are also running, memory pressure can slow the UI. Check:

```bash
docker stats --no-stream
```

If Label Studio's container is using excessive memory, restart it:

```bash
docker compose -f services/label-studio/docker-compose.yml restart label-studio
```

### PostgreSQL connection refused at startup

Label Studio waits for the `postgres` health check but will sometimes fail on first boot if the host machine is slow. Check logs:

```bash
docker compose -f services/label-studio/docker-compose.yml logs label-studio | tail -20
```

If you see "connection refused", restart once — the healthcheck retry window may have been too short:

```bash
docker compose -f services/label-studio/docker-compose.yml restart
```
