#!/bin/sh
set -e

# Explicitly ensure current working directory is on Python path to eliminate ModuleNotFoundError
export PYTHONPATH="."

echo "==> Starting Marzban-style VPN Management Panel..."
echo "==> Environment: PYTHONPATH=${PYTHONPATH}"
echo "==> Port: ${PORT:-8000}"

# Optional build step for frontend if dist folder doesn't exist
if [ -d "frontend" ] && [ ! -d "dist" ] && [ -f "frontend/package.json" ]; then
    echo "==> Building frontend assets..."
    cd frontend && npm install && npm run build && cd ..
    mkdir -p dist
    cp -r frontend/dist/* dist/ || true
fi

# Execute Uvicorn with dynamic port binding for Railway / Docker
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips='*'