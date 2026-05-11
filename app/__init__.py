"""
FitControl Pro 2.0 - Application Entry Point
Premium SaaS Fitness Platform
since 2018 Ailson Soares
"""
import json
import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, render_template, request

from config import get_config
from models import db
from models.user import User
from extensions import login_manager, csrf, migrate, limiter


def _configure_logging(app: Flask) -> None:
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"))
    app.logger.setLevel(log_level)

    log_dir = app.config["LOG_DIR"]
    log_dir.mkdir(parents=True, exist_ok=True)

    if app.config.get("JSON_LOGS"):
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                return json.dumps({
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "path": getattr(record, "path", None),
                    "method": getattr(record, "method", None),
                }, ensure_ascii=False)
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s"
        )

    backend_handler = RotatingFileHandler(
        log_dir / "backend.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    backend_handler.setFormatter(formatter)
    backend_handler.setLevel(log_level)
    app.logger.addHandler(backend_handler)

    auth_logger = logging.getLogger("fitcontrol.auth")
    auth_logger.setLevel(log_level)
    auth_handler = RotatingFileHandler(
        log_dir / "auth.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    auth_handler.setFormatter(formatter)
    auth_logger.addHandler(auth_handler)

    ai_logger = logging.getLogger("fitcontrol.ai")
    ai_logger.setLevel(log_level)
    ai_handler = RotatingFileHandler(
        log_dir / "ai.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    ai_handler.setFormatter(formatter)
    ai_logger.addHandler(ai_handler)

    error_logger = logging.getLogger("fitcontrol.error")
    error_logger.setLevel(logging.ERROR)
    error_handler = RotatingFileHandler(
        log_dir / "error.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
    )
    error_handler.setFormatter(formatter)
    error_logger.addHandler(error_handler)


def _register_blueprints(app: Flask) -> None:
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.alunos import alunos_bp
    from routes.avaliacoes import avaliacoes_bp
    from routes.treinos import treinos_bp
    from routes.protocolos import protocolos_bp
    from routes.relatorios import relatorios_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alunos_bp)
    app.register_blueprint(avaliacoes_bp)
    app.register_blueprint(treinos_bp)
    app.register_blueprint(protocolos_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(api_bp)


def _register_operational_routes(app: Flask) -> None:
    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "app": app.config["APP_NAME"], "version": app.config["APP_VERSION"]})

    @app.get("/readyz")
    def readyz():
        from sqlalchemy import text
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ready"})


def _register_security_headers(app: Flask) -> None:
    @app.after_request
    def apply_security_headers(response):
        if not app.config.get("SECURITY_HEADERS_ENABLED", True):
            return response
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' data: https://fonts.gstatic.com; connect-src 'self'")
        if app.config.get("FORCE_HTTPS") or request.is_secure:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        logging.getLogger("fitcontrol.error").exception("Internal error: %s", error)
        return render_template("errors/500.html"), 500


def _register_context_processors(app: Flask) -> None:
    @app.context_processor
    def inject_globals():
        return {
            "APP_NAME": app.config["APP_NAME"],
            "APP_VERSION": app.config["APP_VERSION"],
            "APP_TAGLINE": app.config["APP_TAGLINE"],
            "current_year": datetime.now(timezone.utc).year,
        }


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False, template_folder="../templates", static_folder="../static")
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    config_class.init_app(app)
    config_class.validate_environment()

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
    _register_operational_routes(app)
    _register_security_headers(app)
    _register_error_handlers(app)
    _register_context_processors(app)

    app.logger.info("FitControl Pro 2.0 initialized.")
    return app


if __name__ == "__main__":
    app = create_app()
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = app.config.get("DEBUG", False)
    app.run(host=host, port=port, debug=debug)
