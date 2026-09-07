# ==============================================================================
# Production Dockerfile for Railway (FastAPI + Static React Dashboard)
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Install build dependencies for postgres and system utils
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

# Copy entire application source (including static/ folder)
COPY . /app

# Ensure both /app/app and /app/backend/app can be resolved
RUN if [ -d "/app/backend/app" ] && [ ! -d "/app/app" ]; then \
        ln -s /app/backend/app /app/app; \
    fi

RUN chmod +x /app/start.sh 2>/dev/null || true

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD ["/bin/sh", "/app/start.sh"]
