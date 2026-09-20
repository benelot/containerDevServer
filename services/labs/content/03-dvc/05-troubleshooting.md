---
title: "Troubleshooting"
weight: 5
---

## Common issues

### `dvc push` fails with "NoSuchBucket"

The MinIO bucket `dvc-cache` must exist. The DVC service compose file creates it automatically, but if the container started before the bucket initialisation completed, the bucket may be missing.

Check:

```bash
docker compose -f services/dvc/docker-compose.yml logs
```

If the bucket creation step failed, recreate it via the MinIO console at **{{< svcurl "dvc_minio_console_port" >}}**: click **Create Bucket** and name it `dvc-cache`.

### `dvc push` says "Everything is up to date" but the file is not in MinIO

DVC uses a local cache at `.dvc/cache` before pushing to the remote. If the push step is skipped, the file may already be in the local cache but not yet in MinIO. Force a push:

```bash
dvc push --run-cache
```

### `dvc pull` downloads the wrong version

Make sure you have checked out the correct `.dvc` pointer file in Git first:

```bash
git log --oneline data/mnist1d_data.pkl.dvc    # see which commits changed the pointer
git checkout <commit> -- data/mnist1d_data.pkl.dvc
dvc pull
```

### Access key errors ("Access Denied")

Credentials are stored per-remote in `.dvc/config.local` (gitignored). If you cloned the repo on a new machine, you need to re-run the `dvc remote modify` credentials commands.

### DVC is not finding the remote

Run `dvc remote list` to see all configured remotes and `dvc remote default` to see which one is active. If `dvc-remote` is not in the list, re-run the `dvc remote add` command from the Setup page.
