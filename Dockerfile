# ==============================================================================
# Stage 1: Build & Dependencies Builder (Multi-Stage)
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system build dependencies required for gRPC, Xray-core tools, and C-extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements file
COPY requirements.txt .

# Install dependencies into an isolated /install directory prefix
RUN pip install --upgrade pip setuptools wheel && \
    pip install --prefix=/install --no-warn-script-location -r requirements.txt

# ==============================================================================
# Stage 2: Minimal Production Runtime for Railway
# ==============================================================================
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/app:/app/backend:/install/lib/python3.11/site-packages" \
    PORT=8000

# Install runtime dependencies (libpq for PostgreSQL, curl for healthcheck, ca-certificates)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage
COPY --from=builder /install /install

# Copy application source code into container
COPY . /app

# Ensure both /app/app and /app/backend/app can be resolved seamlessly
RUN if [ -d "/app/backend/app" ] && [ ! -d "/app/app" ]; then \
        ln -s /app/backend/app /app/app; \
    fi

# Ensure start.sh has execution permissions if present
RUN chmod +x /app/start.sh 2>/dev/null || true

# Railway injects dynamic $PORT at runtime
EXPOSE ${PORT}

# Healthcheck for container orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start the application using Railway dynamic $PORT
CMD ["/bin/sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]