#!/bin/sh
export PYTHONPATH=.

# Ensure index.html is created before app starts
if [ ! -f "app/static/index.html" ] && [ ! -f "static/index.html" ]; then
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        echo "==> Building frontend assets from frontend/ directory..."
        (cd frontend && npm install --silent && npm run build && mkdir -p ../app/static ../static && cp -r dist/* ../app/static/ 2>/dev/null && cp -r dist/* ../static/ 2>/dev/null) || true
    elif [ -f "package.json" ]; then
        echo "==> Building frontend assets from root..."
        (npm install --silent && npm run build && mkdir -p app/static static && cp -r dist/* app/static/ 2>/dev/null && cp -r dist/* static/ 2>/dev/null) || true
    fi
fi

# Synchronize assets between app/static, static, and dist
mkdir -p app/static static dist
if [ -d "app/static" ] && [ -f "app/static/index.html" ]; then
    cp -r app/static/* static/ 2>/dev/null || true
    cp -r app/static/* dist/ 2>/dev/null || true
elif [ -d "static" ] && [ -f "static/index.html" ]; then
    cp -r static/* app/static/ 2>/dev/null || true
    cp -r static/* dist/ 2>/dev/null || true
elif [ -d "dist" ] && [ -f "dist/index.html" ]; then
    cp -r dist/* app/static/ 2>/dev/null || true
    cp -r dist/* static/ 2>/dev/null || true
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"