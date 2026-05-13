#!/usr/bin/env sh
# FitControl Pro 2.0 — Production start script
# Runs DB migrations then starts gunicorn.
set -e

echo "[start.sh] Running database migrations..."
flask db upgrade || echo "[start.sh] WARNING: migrations failed (continuing)"

PORT="${PORT:-5000}"
WORKERS="${WEB_CONCURRENCY:-3}"
THREADS="${GUNICORN_THREADS:-2}"
TIMEOUT="${GUNICORN_TIMEOUT:-60}"

echo "[start.sh] Starting gunicorn on 0.0.0.0:${PORT} (workers=${WORKERS}, threads=${THREADS})"
exec gunicorn wsgi:app \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WORKERS}" \
    --threads "${THREADS}" \
    --timeout "${TIMEOUT}" \
    --access-logfile - \
    --error-logfile -
