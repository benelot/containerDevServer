---
title: "Concept"
weight: 1
---

## Why notebooks exist in ML workflows

Notebooks solve a specific problem: the gap between a question and an answer is often just a few lines of code, but writing those lines in a plain Python script and running it from the command line is slow. You need to see a plot, adjust a parameter, see the plot again, decide something, and move on.

A notebook collapses that loop. Code, output, and prose live in the same document. You can re-run a single cell without losing the state of the others. A visualisation appears inline the moment you generate it.

## What notebooks are not good at

Notebooks are poor production code. They encourage global state, non-linear execution (running cells out of order), and are difficult to test or version meaningfully. The standard pattern in ML is:

1. Prototype in a notebook
2. Extract the proven logic into a function or pipeline asset
3. Run the function at scale in an orchestrator (Dagster, in this stack)

The notebooks in this repo (`mnist1d_crisp_dm.ipynb` and `data_quality.ipynb`) are the prototyping step. The Dagster pipeline is the production step that runs the same logic automatically.

## The JupyterLab environment

This stack uses the `jupyter/datascience-notebook` image, which includes:
- Python, R, and Julia kernels
- NumPy, pandas, matplotlib, seaborn, scikit-learn pre-installed
- Root user access for `pip install` during the session
- The `notebooks/` directory bind-mounted from the repo, so notebooks survive container restarts

MLflow is pre-wired via the `MLFLOW_TRACKING_URI` environment variable. Any `mlflow.*` call in a notebook connects to the MLflow server at `http://host.docker.internal:{{< port "mlflow_port" >}}` automatically.

## host.docker.internal

On Linux, containers do not have `host.docker.internal` available by default. This stack adds it explicitly via `extra_hosts: ["host.docker.internal:host-gateway"]` in the JupyterLab compose file. This means you can always reach services running on the host machine (MLflow, Dagster, etc.) from inside any notebook using `host.docker.internal:<port>`.
