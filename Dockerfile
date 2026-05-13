# ===========================================================================
# FitControl Pro 2.0 — Production Dockerfile
# Multi-stage build: small final image, WeasyPrint system deps included.
# ===========================================================================

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_ENV=production

# WeasyPrint runtime dependencies (cairo, pango, gdk-pixbuf, fonts) + psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libcairo2 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        libffi-dev \
        shared-mime-info \
        fonts-liberation \
        fonts-dejavu \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Create runtime directories and non-root user
RUN mkdir -p /app/instance /app/logs /app/static/uploads \
    && useradd --create-home --shell /bin/bash fitcontrol \
    && chown -R fitcontrol:fitcontrol /app
USER fitcontrol

EXPOSE 5000

# Healthcheck for orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT:-5000}/healthz || exit 1

# Default command — overridable by docker-compose / platform
CMD ["sh", "-c", "./scripts/start.sh"]
