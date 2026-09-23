FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Dagster config at DAGSTER_HOME
COPY dagster.yaml /opt/dagster/dagster.yaml
COPY workspace.yaml /app/workspace.yaml
COPY pipelines/ /app/pipelines/

ENV DAGSTER_HOME=/opt/dagster
