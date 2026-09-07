FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runner
WORKDIR /app
ENV PATH="/install/bin:$PATH" PYTHONPATH="/app:/install/lib/python3.11/site-packages"
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl
COPY --from=builder /install /install
RUN useradd -u 10001 -m appuser
COPY --chown=appuser:appuser . /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]