---
title: "Data Science Labs"
---

# Data Science Labs

Welcome. These labs guide you through a complete machine learning workflow using the Container Dev Server stack — from raw data to a live REST API, with experiment tracking, data quality checks, and production monitoring along the way.

The running example throughout every lab is the **MNIST 1D** dataset: 4000 short time-series sequences representing handwritten digits, each 40 points long. It is small enough to train on a laptop CPU in under a minute, but rich enough to demonstrate every tool in the stack.

## Learning path

| Lab | Tool | What you build |
|---|---|---|
| [Introduction]({{< relref "00-introduction" >}}) | — | CRISP-DM cycle, stack overview, dataset tour |
| [Lab 1]({{< relref "01-mlflow" >}}) | MLflow | Log experiments, compare runs, register a model |
| [Lab 2]({{< relref "02-jupyterlab" >}}) | JupyterLab | Explore the data, train interactively, visualise results |
| [Lab 3]({{< relref "03-dvc" >}}) | DVC | Version the dataset, reproduce any snapshot |
| [Lab 4]({{< relref "04-label-studio" >}}) | Label Studio | Annotate new samples, close the retraining loop |
| [Lab 5]({{< relref "05-dagster" >}}) | Dagster | Run the full pipeline: validate → quality check → train |
| [Lab 6]({{< relref "06-evidently" >}}) | Evidently | Detect data drift, monitor model quality over time |
| [Lab 7]({{< relref "07-bentoml" >}}) | BentoML | Serve the model as a REST API, call it from anywhere |
| [Lab 8]({{< relref "08-monitoring" >}}) | Monitoring | Track hardware health, service uptime, and GPU load |

## Each lab is independent

You can start any lab without completing the ones before it. Every lab includes a **Start here if you skipped earlier labs** section that generates the data and model state it needs in under a minute using the MNIST 1D generator.

If you work through the labs in order, each one picks up where the last left off and you build a single coherent project end to end.

## Before you begin

Make sure the Container Dev Server is cloned and Docker is running. The labs service itself is already running — you are reading this. Start individual service stacks as you enter each lab:

```bash
./scripts/start.sh mlflow      # Lab 1
./scripts/start.sh jupyterlab  # Lab 2
./scripts/start.sh dvc         # Lab 3
./scripts/start.sh label-studio # Lab 4
./scripts/start.sh dagster     # Lab 5
./scripts/start.sh evidently   # Lab 6
./scripts/start.sh bentoml     # Lab 7
./scripts/start.sh monitoring  # Lab 8
```
