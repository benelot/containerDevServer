---
title: "Setup"
weight: 2
---

## Start the DVC remote

```bash
./scripts/start.sh dvc
```

This starts a MinIO instance on port {{< port "dvc_minio_port" >}}. Verify it is healthy:

```bash
curl {{< svcurl "dvc_minio_port" >}}/minio/health/live
# → empty 200 response
```

The MinIO console is at **{{< svcurl "dvc_minio_console_port" >}}** (login: `minioadmin` / `minioadmin_secret`).

## Install DVC

DVC must be installed on your host machine (not inside a container). It is a command-line tool that runs where your code is:

```bash
pip install "dvc[s3]"
dvc --version
```

## Configure the DVC remote

Run these commands from the root of the `containerDevServer` repo:

```bash
dvc remote add -d dvc-remote s3://dvc-cache
dvc remote modify dvc-remote endpointurl  {{< svcurl "dvc_minio_port" >}}
dvc remote modify dvc-remote access_key_id     minioadmin
dvc remote modify dvc-remote secret_access_key minioadmin_secret
```

DVC writes this configuration to `.dvc/config`. Commit it to Git so team members share the same remote:

```bash
git add .dvc/config
git commit -m "Add DVC remote"
```

{{% notice style="info" %}}
The `dvc remote modify` commands store credentials in `.dvc/config.local`, which is gitignored. Team members each run these commands locally; the bucket URL in `.dvc/config` is committed but credentials are not.
{{% /notice %}}

{{% expand title="Start here if you skipped earlier labs" %}}
You only need DVC itself and the MinIO remote running. No prior dataset or model is required.
```bash
pip install "dvc[s3]"
./scripts/start.sh dvc
```
Then configure the remote as shown above.
{{% /expand %}}
