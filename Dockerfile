# Stage 1: Build Frontend Assets (Context-Aware)
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY . .

# Detect frontend location and compile static assets
RUN mkdir -p /build/app/static /build/static /build/dist && \
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then \
        echo "==> Building frontend assets inside frontend/ directory..." && \
        cd frontend && \
        npm install --silent && \
        npm run build && \
        mkdir -p ../app/static ../static && \
        cp -r dist/* ../app/static/ 2>/dev/null || true && \
        cp -r dist/* ../static/ 2>/dev/null || true && \
        cp -r dist/* /build/dist/ 2>/dev/null || true && \
        cd ..; \
    fi && \
    if [ -f "package.json" ]; then \
        echo "==> Building frontend assets from root..." && \
        npm install --silent && \
        npm run build && \
        mkdir -p app/static static && \
        cp -r dist/* app/static/ 2>/dev/null || true && \
        cp -r dist/* static/ 2>/dev/null || true && \
        cp -r dist/* /build/dist/ 2>/dev/null || true; \
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
COPY --from=frontend-builder /build/app/static ./app/static
RUN chmod +x /app/start.sh && \
    chmod -R 755 /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]