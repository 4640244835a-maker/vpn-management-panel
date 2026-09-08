# Stage 1: Build Frontend Assets
FROM node:20-alpine AS frontend-builder
WORKDIR /build
COPY package.json tsconfig*.json vite.config.ts index.html ./
COPY src/ ./src/
COPY public/ ./public/
RUN npm install --silent && npm run build

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
RUN chmod +x /app/start.sh && \
    chmod -R 755 /app
EXPOSE 8000
CMD ["/bin/sh", "/app/start.sh"]