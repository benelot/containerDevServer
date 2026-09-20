#!/usr/bin/env python3
"""Reads service port env vars and writes data/ports.yaml for Hugo."""
import os

PORTS = {
    "mlflow_port":              os.environ.get("MLFLOW_PORT",                "5000"),
    "mlflow_postgres_port":     os.environ.get("MLFLOW_POSTGRES_PORT",       "5432"),
    "mlflow_minio_port":        os.environ.get("MLFLOW_MINIO_PORT",          "9000"),
    "mlflow_minio_console_port":os.environ.get("MLFLOW_MINIO_CONSOLE_PORT",  "9001"),
    "dvc_minio_port":           os.environ.get("DVC_MINIO_PORT",             "9010"),
    "dvc_minio_console_port":   os.environ.get("DVC_MINIO_CONSOLE_PORT",     "9011"),
    "label_studio_port":        os.environ.get("LABEL_STUDIO_PORT",          "8080"),
    "label_studio_postgres_port":os.environ.get("LABEL_STUDIO_POSTGRES_PORT","5433"),
    "jupyter_port":             os.environ.get("JUPYTER_PORT",               "8888"),
    "dagster_port":             os.environ.get("DAGSTER_PORT",               "3000"),
    "dagster_postgres_port":    os.environ.get("DAGSTER_POSTGRES_PORT",      "5434"),
    "evidently_port":           os.environ.get("EVIDENTLY_PORT",             "8001"),
    "bentoml_port":             os.environ.get("BENTOML_PORT",               "3001"),
    "grafana_port":             os.environ.get("GRAFANA_PORT",               "3002"),
    "prometheus_port":          os.environ.get("PROMETHEUS_PORT",            "9090"),
    "cadvisor_port":            os.environ.get("CADVISOR_PORT",              "8082"),
    "labs_port":                os.environ.get("LABS_PORT",                  "3003"),
}

out = "\n".join(f"{k}: {v}" for k, v in PORTS.items()) + "\n"
data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(data_dir, exist_ok=True)
path = os.path.join(data_dir, "ports.yaml")
with open(path, "w") as f:
    f.write(out)
print(f"Wrote {path}")
