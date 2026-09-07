#!/bin/sh
set -e

echo "=== Starting FastAPI + Xray Backend on Railway ==="

# Railway dynamically injects $PORT (default to 8000 if not set)
PORT="${PORT:-8000}"
echo "Target port: $PORT"

# Ensure global python environment has uvicorn installed
if ! command -v uvicorn >/dev/null 2>&1; then
    echo "Uvicorn not found in PATH! Installing requirements globally..."
    pip install --no-cache-dir -r /app/requirements.txt || pip install --no-cache-dir uvicorn[standard] fastapi
fi

# Ensure both "app" and "backend.app" are importable in any directory structure
if [ -d "/app/backend/app" ] && [ ! -d "/app/app" ] && [ ! -L "/app/app" ]; then
    ln -s /app/backend/app /app/app || true
fi

# Export PYTHONPATH to ensure all modules are found
export PYTHONPATH="/app:/app/backend:${PYTHONPATH}"

# Run database migrations if alembic config exists
if [ -f "alembic.ini" ] || [ -f "backend/alembic.ini" ]; then
    echo "Applying database migrations..."
    alembic upgrade head || echo "Alembic step skipped"
fi

echo "Launching Uvicorn on 0.0.0.0:$PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
