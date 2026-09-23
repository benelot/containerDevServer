#!/bin/bash
set -euo pipefail

echo "==> Generating port data from environment..."
python3 /app/scripts/generate_ports_data.py

echo "==> Building Hugo site..."
cd /app
hugo --minify --destination /app/public

echo "==> Starting FastAPI..."
exec uvicorn main:app --host 0.0.0.0 --port "${LABS_PORT:-3003}"
