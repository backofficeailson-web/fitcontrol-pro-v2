"""Health and readiness endpoints for cloud platforms / load balancers."""
from __future__ import annotations

from datetime import datetime, UTC

from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from models import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/healthz")
def healthz():
    """Liveness probe — process is up and responding."""
    return jsonify(
        {
            "status": "ok",
            "service": current_app.config["APP_NAME"],
            "version": current_app.config["APP_VERSION"],
            "time": datetime.now(UTC).isoformat() + "Z",
        }
    ), 200


@health_bp.route("/readyz")
def readyz():
    """Readiness probe — DB reachable and accepting connections."""
    db_ok = True
    db_error: str | None = None
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        db_ok = False
        db_error = str(exc)
        current_app.logger.error("Readiness DB check failed: %s", exc)

    payload = {
        "status": "ready" if db_ok else "not-ready",
        "database": "ok" if db_ok else "error",
        "time": datetime.now(UTC).isoformat() + "Z",
    }
    if db_error and current_app.config.get("DEBUG"):
        payload["error"] = db_error
    return jsonify(payload), (200 if db_ok else 503)
