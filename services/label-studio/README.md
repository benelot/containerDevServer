# Label Studio

Web-based data annotation tool for the CRISP-DM Data Understanding and Deployment phases.

## CRISP-DM role

| Phase | Contribution |
|---|---|
| Data Understanding | Manually review and annotate a representative sample before any modelling |
| Deployment | Re-label samples flagged for drift by Evidently; feed them back into the training pipeline |

The second use is the feedback loop that keeps a deployed model accurate over time: Evidently detects distribution shift in production data → new samples are exported to Label Studio for re-labeling → the corrected annotations are versioned with DVC → the Dagster pipeline retrains the model → BentoML loads the updated Production model.

## Quickstart

```bash
./scripts/start.sh label-studio
# http://localhost:8080
# Login: admin@example.com / changeme  (set LABEL_STUDIO_PASSWORD in .env)
```

## Typical workflow

1. Create a project in the Label Studio UI and configure the labeling interface.
2. Import your dataset (CSV, JSON, or image files).
3. Annotate samples in the browser.
4. Export annotations as JSON or CSV.
5. Version the export with DVC: `dvc add annotations/export.json && dvc push`.
6. Reference the versioned annotation file in the Dagster pipeline.

## Services

| Container | Port | Purpose |
|---|---|---|
| `label-studio` | 8080 | Label Studio web UI |
| `label-studio-db` | 5433 | PostgreSQL — project and annotation metadata |

## Configuration

| Variable | Default | Description |
|---|---|---|
| `LABEL_STUDIO_PORT` | `8080` | Web UI port |
| `POSTGRES_PORT` | `5433` | PostgreSQL port (offset from MLflow's 5432) |
| `LABEL_STUDIO_USERNAME` | `admin@example.com` | Initial admin login |
| `LABEL_STUDIO_PASSWORD` | `changeme` | Initial admin password — change before production use |
