# Label Studio

## What it does

[Label Studio](https://labelstud.io) is an open-source data annotation tool. It provides a web UI for humans to label images, text, audio, time series, and structured data. Output is standard JSON that can feed directly into a training pipeline.

Key capabilities relevant to this stack:

- **Multi-modal annotation** -- images, sequences, text classification, named entity recognition, bounding boxes, polygons
- **Pre-annotation** -- run a model first and have annotators correct its predictions (active learning loop)
- **Agreement metrics** -- when multiple annotators label the same item, measure inter-annotator agreement
- **Export formats** -- JSON, CSV, COCO, YOLO, Pascal VOC, and more

## Architecture in this stack

Label Studio stores project configuration and annotation data in PostgreSQL. This is preferred over the default SQLite because:

- The annotation database is shared and survives container restarts cleanly
- PostgreSQL supports larger concurrent annotation teams
- Backup is straightforward with standard `pg_dump`

A dedicated PostgreSQL instance runs on port 5433 to avoid conflict with the MLflow PostgreSQL on 5432.

## Default ports

| Service | Port | Variable |
|---|---|---|
| Label Studio UI | 8080 | `LABEL_STUDIO_PORT` |
| PostgreSQL | 5433 | `POSTGRES_PORT` |

Default login: set in `.env` (default `admin@example.com` / `changeme`).

## Quick start

```bash
./scripts/start.sh label-studio
# Open http://localhost:8080 and log in
# Create a project, upload data, and start annotating
```

After annotating, export and version the labeled dataset with DVC:

```bash
dvc add data/labeled/annotations.json
git add data/labeled/annotations.json.dvc
git commit -m "add v1 labeled dataset"
dvc push
```

## CRISP-DM role

Label Studio is primarily a **Data Understanding** and **Data Preparation** tool.

| Phase | What Label Studio provides |
|---|---|
| Business Understanding | Define what correct labels look like; forces early agreement on the prediction target |
| Data Understanding | Manual inspection of raw samples surfaces quality issues (duplicates, corrupted files, ambiguous cases) before training |
| Data Preparation | Produce clean, consistent labels that form the ground truth for supervised learning |
| Evaluation | Re-annotate a held-out test set to verify the model's errors are real errors, not labeling noise |

In a real project the labeling process is not a one-time step. As the model improves and finds hard cases, those cases cycle back to Label Studio for re-labeling. Label Studio is the entry point of that active learning loop.
