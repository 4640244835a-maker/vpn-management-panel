#!/bin/sh
set -e

echo "=== Starting FastAPI + React Dashboard on Railway ==="
export PYTHONPATH=.

# Verify static directory exists for serving
if [ -d "static" ]; then
    echo "Static UI directory found with $(ls static | wc -l) files."
fi

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
