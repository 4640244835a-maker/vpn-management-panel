# Stage 1: Build Frontend Assets (Context-Aware)
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY . .

RUN mkdir -p /build/dist /build/static && \
    if [ -f "package.json" ]; then \
        echo "==> Detected package.json at root. Building frontend..." && \
        mkdir -p public && \
        npm install --silent && \
        npm run build --if-present && \
        if [ -d "dist" ]; then cp -r dist/* /build/dist/ 2>/dev/null || true; cp -r dist/* /build/static/ 2>/dev/null || true; fi; \
        if [ -d "static" ]; then cp -r static/* /build/static/ 2>/dev/null || true; fi; \
    elif [ -d "frontend" ] && [ -f "frontend/package.json" ]; then \
        echo "==> Detected frontend/ directory. Building assets..." && \
        cd frontend && \
        mkdir -p public && \
        npm install --silent && \
        npm run build --if-present && \
        if [ -d "dist" ]; then cp -r dist/* /build/dist/ 2>/dev/null || true; cp -r dist/* /build/static/ 2>/dev/null || true; fi; \
        if [ -d "static" ]; then cp -r static/* /build/static/ 2>/dev/null || true; fi && \
        cd ..; \
    else \
        echo "==> No frontend package.json found. Creating placeholder..." && \
        echo '<!DOCTYPE html><html><head><meta charset="utf-8"><title>API Running</title></head><body><h2>FastAPI Backend Running</h2><p><a href="/docs">Docs</a></p></body></html>' > /build/dist/index.html && \
        cp /build/dist/index.html /build/static/index.html; \
    fi

# Stage 2: Final Production Python Image
FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="."
WORKDIR /app
RUN apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY start.sh .
COPY --from=frontend-builder /build/dist ./dist
COPY --from=frontend-builder /build/static ./static
RUN chmod +x /app/start.sh && \
    chmod -R 755 /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]