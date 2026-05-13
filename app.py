"""
FitControl Pro 2.0 - Application Entry Point
Premium SaaS Fitness Platform — Cloud, Mobile & Network Production Ready
since 2018 Ailson Soares
"""
from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, render_template, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from config import get_config
from models import db
from models.user import User
from extensions import login_manager, csrf, migrate, limiter


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def _configure_logging(app: Flask) -> None:
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)
    app.logger.setLevel(log_level)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s"
    )

    # In production cloud platforms (Render/Railway/Fly/Heroku) we log to stdout
    if app.config.get("LOG_TO_STDOUT"):
        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(formatter)
        stream.setLevel(log_level)
        # Avoid duplicate stdout handlers
        if not any(isinstance(h, logging.StreamHandler) for h in app.logger.handlers):
            app.logger.addHandler(stream)

    # File logs only when LOG_DIR is writable (local dev / containers with mounted volume)
    log_dir = app.config.get("LOG_DIR")
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        for name in ("backend", "auth", "ai", "error"):
            target_logger = (
                app.logger if name == "backend" else logging.getLogger(f"fitcontrol.{name}")
            )
            level = logging.ERROR if name == "error" else log_level
            target_logger.setLevel(level)
            handler = RotatingFileHandler(
                log_dir / f"{name}.log",
                maxBytes=2_000_000,
                backupCount=5,
                encoding="utf-8",
            )
            handler.setFormatter(formatter)
            handler.setLevel(level)
            target_logger.addHandler(handler)
    except (OSError, PermissionError) as exc:
        app.logger.warning("File logging disabled: %s", exc)


# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------
def _register_blueprints(app: Flask) -> None:
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.alunos import alunos_bp
    from routes.avaliacoes import avaliacoes_bp
    from routes.treinos import treinos_bp
    from routes.protocolos import protocolos_bp
    from routes.relatorios import relatorios_bp
    from routes.api import api_bp
    from routes.health import health_bp
    from routes.pwa import pwa_bp
    from routes.postura import postura_bp
    from routes.ai_lab import ai_lab_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alunos_bp)
    app.register_blueprint(avaliacoes_bp)
    app.register_blueprint(treinos_bp)
    app.register_blueprint(protocolos_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(pwa_bp)
    app.register_blueprint(postura_bp)
    app.register_blueprint(ai_lab_bp)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(413)
    def too_large(_error):
        return render_template("errors/500.html"), 413

    @app.errorhandler(500)
    def internal_error(error):
        logging.getLogger("fitcontrol.error").exception("Internal error: %s", error)
        return render_template("errors/500.html"), 500


# ---------------------------------------------------------------------------
# Context processors
# ---------------------------------------------------------------------------
def _register_context_processors(app: Flask) -> None:
    from datetime import datetime, UTC

    @app.context_processor
    def inject_globals():
        return {
            "APP_NAME": app.config["APP_NAME"],
            "APP_VERSION": app.config["APP_VERSION"],
            "APP_TAGLINE": app.config["APP_TAGLINE"],
            "current_year": datetime.now(UTC).year,
        }


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------
def _register_security_headers(app: Flask) -> None:
    if not app.config.get("ENABLE_SECURITY_HEADERS", True):
        return

    csp = app.config.get("CONTENT_SECURITY_POLICY")

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=()",
        )
        if csp:
            response.headers.setdefault("Content-Security-Policy", csp)
        # HSTS only when we're sure we're on HTTPS (production behind proxy)
        if app.config.get("SESSION_COOKIE_SECURE"):
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Reverse proxy fix (Render/Railway/Fly/Heroku/Nginx)
    if app.config.get("BEHIND_PROXY"):
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Você precisa estar autenticado para acessar esta área."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    _configure_logging(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_context_processors(app)
    _register_security_headers(app)

    # Friendly favicon route (avoids noisy 404s in logs)
    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            app.static_folder, "img/favicon.ico", mimetype="image/x-icon"
        )

    app.logger.info(
        "FitControl Pro %s initialized [env=%s, db=%s]",
        app.config["APP_VERSION"],
        os.getenv("FLASK_ENV", "development"),
        "postgres" if "postgres" in app.config["SQLALCHEMY_DATABASE_URI"] else "sqlite",
    )
    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", "5000")))
    debug = app.config.get("DEBUG", False)
    app.run(host=host, port=port, debug=debug)
