# ==============================================================================
# Production Dockerfile for Railway (Global Python Environment)
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Install system build dependencies required for gRPC, Xray-core tools, and C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpq5 \
    gcc \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel in global environment
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements file first for Docker layer caching
COPY requirements.txt .

# Install dependencies directly into the global Python environment
RUN pip install --no-cache-dir -r requirements.txt

# Verify global uvicorn installation
RUN which uvicorn && uvicorn --version

# Copy the application source code
COPY . /app

# Ensure both /app/app and /app/backend/app can be resolved seamlessly
RUN if [ -d "/app/backend/app" ] && [ ! -d "/app/app" ]; then \
        ln -s /app/backend/app /app/app; \
    fi

# Ensure start.sh has execution permissions
RUN chmod +x /app/start.sh 2>/dev/null || true

# Railway injects dynamic $PORT at runtime
EXPOSE ${PORT}

# Healthcheck for container orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start the application via startup script
CMD ["/bin/sh", "/app/start.sh"]
