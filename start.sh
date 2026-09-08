#!/bin/sh
export PYTHONPATH=.

if [ -d "dist" ] && [ ! -d "static" ]; then
    cp -r dist static 2>/dev/null || true
elif [ -d "static" ] && [ ! -d "dist" ]; then
    cp -r static dist 2>/dev/null || true
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"