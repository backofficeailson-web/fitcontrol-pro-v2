#!/usr/bin/env sh
# FitControl Pro 2.0 — Release phase script
# Used by Heroku/Railway/Render to run DB migrations BEFORE traffic flips.
set -e

echo "[release.sh] Applying database migrations..."
flask db upgrade

echo "[release.sh] Release complete."
