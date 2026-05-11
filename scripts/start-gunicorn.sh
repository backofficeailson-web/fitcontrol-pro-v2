#!/usr/bin/env bash
set -euo pipefail
flask db upgrade
gunicorn --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --threads ${WEB_THREADS:-4} --timeout 120 wsgi:app
