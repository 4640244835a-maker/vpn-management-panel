# ==============================================================================
# Stage 1: Build React Dashboard Frontend
# ==============================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend

# Copy package descriptors if frontend directory exists or copy root package.json
COPY package*.json ./
RUN if [ -f "package.json" ]; then npm install --legacy-peer-deps || true; fi

# Copy frontend source files
COPY . .
ENV VITE_API_BASE_URL="https://ali-production-6799.up.railway.app/api"
RUN if [ -f "package.json" ]; then npm run build 2>/dev/null || mkdir -p dist; else mkdir -p dist; fi

# ==============================================================================
# Stage 2: Production Python Runtime with Integrated Static Frontend
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Install system build dependencies required for gRPC and postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpq5 \
    gcc \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify global uvicorn installation
RUN which uvicorn && uvicorn --version

# Copy backend application source code
COPY . /app

# Copy compiled static frontend into /app/static for FastAPI FileResponse / StaticFiles
COPY --from=frontend-builder /frontend/dist /app/static

# Ensure both /app/app and /app/backend/app can be resolved seamlessly
RUN if [ -d "/app/backend/app" ] && [ ! -d "/app/app" ]; then \
        ln -s /app/backend/app /app/app; \
    fi

RUN chmod +x /app/start.sh 2>/dev/null || true

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD ["/bin/sh", "/app/start.sh"]
