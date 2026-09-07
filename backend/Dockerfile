# Production Dockerfile for Railway backend
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify uvicorn
RUN which uvicorn && uvicorn --version

COPY . /app

# Ensure symlink for module imports
RUN if [ -d "/app/app" ] && [ ! -d "/app/backend" ]; then \
        mkdir -p /app/backend && ln -s /app/app /app/backend/app; \
    fi

ENV PYTHONPATH="/app:/app/backend:${PYTHONPATH}"

EXPOSE ${PORT}

CMD ["/bin/sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
