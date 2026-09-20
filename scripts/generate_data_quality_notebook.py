#!/usr/bin/env python3
"""Generates notebooks/data_quality.ipynb."""
import json, os

os.makedirs("notebooks", exist_ok=True)

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}

def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source}

cells = []

# ── Title ─────────────────────────────────────────────────────────────────────
cells.append(md(
    "# Data Quality & Validation — Pandera, DeepChecks, Evidently, Pointblank\n"
    "\n"
    "This notebook validates the MNIST 1D dataset and trained model against the full quality stack:\n"
    "\n"
    "| Tool | Purpose | Status |\n"
    "|---|---|---|\n"
    "| **Pandera** | Schema validation — feature ranges, label domain, null checks | Recommended for ML |\n"
    "| **DeepChecks** | Dataset integrity + train/test distribution suites | ML-specific checks |\n"
    "| **Evidently** | Data drift + quality HTML reports → logged to MLflow/MinIO | Monitoring |\n"
    "| **Pointblank** | Interactive stakeholder-facing data quality reports | New (2024) |\n"
    "| Great Expectations | Enterprise governance, Data Docs | Use if team needs GX Cloud |\n"
    "\n"
    "> **Run this notebook after** `mnist1d_crisp_dm.ipynb` so `best_model.pt` and the dataset exist.\n"
))

# ── Install ───────────────────────────────────────────────────────────────────
cells.append(code(
    "import subprocess, sys\n"
    "packages = ['pandera', 'deepchecks', 'evidently', 'pointblank', 'mlflow', 'boto3']\n"
    "subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', '--upgrade'] + packages)\n"
    "print('Ready.')\n"
))

# ── Config + load data ────────────────────────────────────────────────────────
cells.append(code(
    "import os, pickle, warnings\n"
    "import numpy as np\n"
    "import pandas as pd\n"
    "import torch\n"
    "import torch.nn as nn\n"
    "import mlflow\n"
    "warnings.filterwarnings('ignore')\n"
    "\n"
    "MLFLOW_TRACKING_URI = os.environ.get('MLFLOW_TRACKING_URI', 'http://localhost:5000')\n"
    "SEED = 42\n"
    "\n"
    "with open('mnist1d_data.pkl', 'rb') as f:\n"
    "    data = pickle.load(f)\n"
    "\n"
    "X_train = np.array(data['x'],      dtype=np.float32)\n"
    "y_train = np.array(data['y'],      dtype=np.int64)\n"
    "X_test  = np.array(data['x_test'], dtype=np.float32)\n"
    "y_test  = np.array(data['y_test'], dtype=np.int64)\n"
    "\n"
    "N_FEATURES = X_train.shape[1]   # 40\n"
    "COLS = [f't{i}' for i in range(N_FEATURES)]\n"
    "\n"
    "df_train = pd.DataFrame(X_train, columns=COLS)\n"
    "df_train['label'] = y_train\n"
    "df_test  = pd.DataFrame(X_test,  columns=COLS)\n"
    "df_test['label']  = y_test\n"
    "\n"
    "print(f'Train: {df_train.shape}  Test: {df_test.shape}')\n"
))

# ── § 1 Pandera ────────────────────────────────────────────────────────────────
cells.append(md(
    "## § 1 Pandera — Schema Validation\n"
    "\n"
    "Pandera enforces contracts on DataFrames at code time (or at runtime as a decorator). "
    "It is the recommended replacement for Great Expectations in Python ML pipelines — simpler API, "
    "no YAML, native pandas/Polars/Pyspark support.\n"
))

cells.append(code(
    "import pandera as pa\n"
    "\n"
    "# ── Define schema ────────────────────────────────────────────────────────\n"
    "feature_checks = {c: pa.Column(float, pa.Check.between(-8.0, 8.0), nullable=False) for c in COLS}\n"
    "feature_checks['label'] = pa.Column(int, pa.Check.isin(list(range(10))), nullable=False)\n"
    "\n"
    "schema = pa.DataFrameSchema(\n"
    "    feature_checks,\n"
    "    coerce=True,\n"
    "    strict=False,       # allow extra columns (future-proof)\n"
    ")\n"
    "\n"
    "# ── Run validation ────────────────────────────────────────────────────────\n"
    "try:\n"
    "    schema.validate(df_train, lazy=True)   # lazy=True collects all errors\n"
    "    print(f'Train schema  PASS  ({len(df_train):,} rows)')\n"
    "except pa.errors.SchemaErrors as e:\n"
    "    print('Train schema  FAIL')\n"
    "    print(e.failure_cases.head())\n"
    "\n"
    "try:\n"
    "    schema.validate(df_test, lazy=True)\n"
    "    print(f'Test  schema  PASS  ({len(df_test):,} rows)')\n"
    "except pa.errors.SchemaErrors as e:\n"
    "    print('Test  schema  FAIL')\n"
    "    print(e.failure_cases.head())\n"
))

cells.append(code(
    "# ── Class-based schema (alternative, supports type annotations) ──────────\n"
    "class Mnist1DSchema(pa.DataFrameModel):\n"
    "    label: pa.typing.Series[int] = pa.Field(isin=list(range(10)))\n"
    "\n"
    "    class Config:\n"
    "        coerce = True\n"
    "\n"
    "validated_df = Mnist1DSchema.validate(df_train)\n"
    "print(f'Class-based schema PASS  shape={validated_df.shape}')\n"
))

# ── § 2 DeepChecks ────────────────────────────────────────────────────────────
cells.append(md(
    "## § 2 DeepChecks — Dataset Integrity & Train/Test Validation\n"
    "\n"
    "DeepChecks runs suites of checks that are specific to ML: "
    "feature drift, label drift, label ambiguity, duplicate samples, and more. "
    "Results are interactive HTML reports.\n"
))

cells.append(code(
    "from deepchecks.tabular import Dataset\n"
    "from deepchecks.tabular.suites import data_integrity, train_test_validation\n"
    "\n"
    "train_ds = Dataset(df_train, label='label', cat_features=[])\n"
    "test_ds  = Dataset(df_test,  label='label', cat_features=[])\n"
    "\n"
    "print('Running data integrity suite on training set...')\n"
    "integrity_result = data_integrity().run(train_ds)\n"
    "integrity_result.save_as_html('deepchecks_integrity.html')\n"
    "print('Saved: deepchecks_integrity.html')\n"
    "\n"
    "print('Running train/test validation suite...')\n"
    "tt_result = train_test_validation().run(train_ds, test_ds)\n"
    "tt_result.save_as_html('deepchecks_train_test.html')\n"
    "print('Saved: deepchecks_train_test.html')\n"
))

cells.append(code(
    "# Show inline summary\n"
    "print('=== Data integrity: passed / failed checks ===')\n"
    "for check_result in integrity_result.get_not_passed_checks():\n"
    "    print(f'  FAIL  {check_result.get_header()}')\n"
    "passed = len(integrity_result.get_passed_checks())\n"
    "failed = len(integrity_result.get_not_passed_checks())\n"
    "print(f'  {passed} passed  {failed} failed')\n"
    "\n"
    "print()\n"
    "print('=== Train/test: passed / failed checks ===')\n"
    "for check_result in tt_result.get_not_passed_checks():\n"
    "    print(f'  FAIL  {check_result.get_header()}')\n"
    "passed2 = len(tt_result.get_passed_checks())\n"
    "failed2 = len(tt_result.get_not_passed_checks())\n"
    "print(f'  {passed2} passed  {failed2} failed')\n"
))

cells.append(code(
    "# Log DeepChecks reports to MLflow\n"
    "mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)\n"
    "mlflow.set_experiment('mnist1d-quality')\n"
    "\n"
    "with mlflow.start_run(run_name='deepchecks') as run:\n"
    "    mlflow.log_metric('integrity_passed', passed)\n"
    "    mlflow.log_metric('integrity_failed', failed)\n"
    "    mlflow.log_metric('traintest_passed', passed2)\n"
    "    mlflow.log_metric('traintest_failed', failed2)\n"
    "    mlflow.log_artifact('deepchecks_integrity.html')\n"
    "    mlflow.log_artifact('deepchecks_train_test.html')\n"
    "    QUALITY_RUN_ID = run.info.run_id\n"
    "\n"
    "print(f'DeepChecks reports logged — run {QUALITY_RUN_ID}')\n"
))

# ── § 3 Evidently ─────────────────────────────────────────────────────────────
cells.append(md(
    "## § 3 Evidently AI — Data Drift & Quality Reports\n"
    "\n"
    "Evidently generates rich HTML reports and JSON snapshots. "
    "Snapshots can be pushed to the `evidently` container's workspace for persistent monitoring. "
    "Here we generate a drift report (train as reference, test as current data) and log it to MLflow.\n"
))

cells.append(code(
    "from evidently.report import Report\n"
    "from evidently.metric_preset import DataDriftPreset, DataQualityPreset\n"
    "from evidently.test_suite import TestSuite\n"
    "from evidently.test_preset import DataStabilityTestPreset, NoTargetPerformanceTestPreset\n"
    "\n"
    "# HTML report\n"
    "report = Report(metrics=[DataQualityPreset(), DataDriftPreset()])\n"
    "report.run(reference_data=df_train, current_data=df_test)\n"
    "report.save_html('evidently_drift_report.html')\n"
    "print('Saved: evidently_drift_report.html')\n"
    "\n"
    "# Test suite (pass/fail assertions)\n"
    "suite = TestSuite(tests=[DataStabilityTestPreset()])\n"
    "suite.run(reference_data=df_train, current_data=df_test)\n"
    "suite.save_html('evidently_tests.html')\n"
    "print('Saved: evidently_tests.html')\n"
))

cells.append(code(
    "# Log to MLflow\n"
    "with mlflow.start_run(run_id=QUALITY_RUN_ID):\n"
    "    mlflow.log_artifact('evidently_drift_report.html')\n"
    "    mlflow.log_artifact('evidently_tests.html')\n"
    "    # Log pass/fail counts from the test suite\n"
    "    results = suite.as_dict()\n"
    "    n_passed = sum(1 for t in results.get('tests', []) if t.get('status') == 'SUCCESS')\n"
    "    n_failed = sum(1 for t in results.get('tests', []) if t.get('status') == 'FAIL')\n"
    "    mlflow.log_metric('evidently_tests_passed', n_passed)\n"
    "    mlflow.log_metric('evidently_tests_failed', n_failed)\n"
    "print(f'Evidently: {n_passed} tests passed  {n_failed} failed')\n"
    "print(f'Reports logged to MLflow run {QUALITY_RUN_ID}')\n"
))

cells.append(code(
    "# ── Optional: push snapshot to the Evidently monitoring service ──────────\n"
    "# Requires the 'evidently' service stack to be running (./scripts/start.sh evidently)\n"
    "EVIDENTLY_SERVICE_URL = os.environ.get('EVIDENTLY_SERVICE_URL', 'http://localhost:8001')\n"
    "\n"
    "try:\n"
    "    from evidently.ui.workspace.cloud import CloudWorkspace\n"
    "    ws = CloudWorkspace(token='', url=EVIDENTLY_SERVICE_URL)  # no auth for self-hosted\n"
    "    project = ws.create_project('MNIST 1D monitoring')\n"
    "    project.save()\n"
    "    ws.add_report(project.id, report)\n"
    "    print(f'Snapshot pushed to Evidently service at {EVIDENTLY_SERVICE_URL}')\n"
    "except Exception as e:\n"
    "    print(f'Evidently service not reachable ({e!r}) — report is still in MLflow.')\n"
))

# ── § 4 Pointblank ────────────────────────────────────────────────────────────
cells.append(md(
    "## § 4 Pointblank — Interactive Data Quality Reports (New, 2024)\n"
    "\n"
    "[Pointblank](https://github.com/posit-dev/pointblank) is a 2024 release from Posit "
    "(makers of RStudio/Tidyverse). It produces beautiful, interactive validation reports for "
    "pandas and Polars DataFrames. Designed for stakeholder-facing quality reviews.\n"
    "\n"
    "Compared to Great Expectations: simpler API, no YAML, better visualisation, "
    "no server required. Best for batch reports. GX is better if you need enterprise "
    "data governance, Data Docs, and integration with Airflow/dbt at scale.\n"
))

cells.append(code(
    "import pointblank as pb\n"
    "\n"
    "# ── Build a validation plan ───────────────────────────────────────────────\n"
    "v = (\n"
    "    pb.Validate(df_train, tbl_name='MNIST1D-train', label='Data Quality Check')\n"
    "    .col_vals_not_null(columns=COLS + ['label'])\n"
    "    .col_vals_between(columns=COLS, left=-8.0, right=8.0)\n"
    "    .col_vals_in_set(columns=['label'], set=list(range(10)))\n"
    "    .col_count_match(count=N_FEATURES + 1)   # 40 features + label\n"
    "    .row_count_match(count=4000)\n"
    "    .interrogate()\n"
    ")\n"
    "\n"
    "print(v)\n"
))

cells.append(code(
    "# Export Pointblank report to HTML and log to MLflow\n"
    "pb_html = 'pointblank_report.html'\n"
    "v.get_tabular_report().write_html(pb_html)\n"
    "print(f'Saved: {pb_html}')\n"
    "\n"
    "with mlflow.start_run(run_id=QUALITY_RUN_ID):\n"
    "    mlflow.log_artifact(pb_html)\n"
    "print(f'Pointblank report logged to MLflow run {QUALITY_RUN_ID}')\n"
))

# ── § 5 Great Expectations (brief) ────────────────────────────────────────────
cells.append(md(
    "## § 5 Great Expectations v1 (reference)\n"
    "\n"
    "GX is still the right choice when you need:\n"
    "- Team-shared Data Docs hosted as static sites\n"
    "- Integration with dbt or Airflow checkpoints at enterprise scale\n"
    "- GX Cloud for centralised governance\n"
    "\n"
    "For this stack (DataFrame-centric ML), Pandera covers the same validation "
    "with far less boilerplate. The snippet below shows the GX v1 Python Fluent API "
    "(v1.0 dropped most of the YAML in August 2024).\n"
))

cells.append(code(
    "# GX v1 Fluent API — install with: pip install great-expectations\n"
    "# (Not run by default; uncomment to use)\n"
    "\n"
    "# import great_expectations as gx\n"
    "#\n"
    "# ctx = gx.get_context(mode='ephemeral')\n"
    "# ds  = ctx.data_sources.add_pandas('mnist1d')\n"
    "# da  = ds.add_dataframe_asset('train')\n"
    "# batch = da.add_batch_definition_whole_dataframe('all').get_batch(batch_parameters={'dataframe': df_train})\n"
    "#\n"
    "# suite = ctx.suites.add(gx.ExpectationSuite(name='mnist1d_suite'))\n"
    "# suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column='label'))\n"
    "# suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(\n"
    "#     column='t0', min_value=-8.0, max_value=8.0))\n"
    "#\n"
    "# results = batch.validate(suite)\n"
    "# print(results)\n"
    "print('GX snippet is commented out. Install great-expectations and uncomment to run.')\n"
))

# ── Summary ────────────────────────────────────────────────────────────────────
cells.append(md(
    "## Summary\n"
    "\n"
    "| Run this notebook gets you | Stored in |\n"
    "|---|---|\n"
    "| Pandera schema pass/fail | console |\n"
    "| DeepChecks integrity HTML | MLflow artifact (MinIO) |\n"
    "| DeepChecks train/test HTML | MLflow artifact (MinIO) |\n"
    "| Evidently drift report HTML | MLflow artifact (MinIO) + Evidently service |\n"
    "| Evidently test suite HTML | MLflow artifact (MinIO) |\n"
    "| Pointblank interactive report HTML | MLflow artifact (MinIO) |\n"
    "\n"
    "The same validation logic runs inside the Dagster pipeline "
    "(`services/dagster/pipelines/mnist1d_pipeline.py`) automatically when you trigger "
    "`mnist1d_full_pipeline` from the Dagster UI (`http://localhost:3000`).\n"
))

# ── Write file ─────────────────────────────────────────────────────────────────
notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"},
    },
    "cells": cells,
}

out = "notebooks/data_quality.ipynb"
with open(out, "w") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)
print(f"Generated {out}  ({os.path.getsize(out):,} bytes)")
