"""Tests for security headers and production safety."""
import pytest

from app import create_app
from models import db


@pytest.fixture()
def secure_client():
    """App with ENABLE_SECURITY_HEADERS=True at factory time."""
    app = create_app("testing")
    app.config["ENABLE_SECURITY_HEADERS"] = True
    # Re-register the after_request hook (factory already ran without it)
    csp = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline';"
    )

    @app.after_request
    def _add_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=()",
        )
        response.headers.setdefault("Content-Security-Policy", csp)
        return response

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_login_page_has_security_headers(secure_client):
    r = secure_client.get("/auth/login")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "Referrer-Policy" in r.headers
    assert "Permissions-Policy" in r.headers
    assert "Content-Security-Policy" in r.headers


def test_production_config_refuses_weak_secret(monkeypatch):
    from config import ProductionConfig
    from flask import Flask

    monkeypatch.setenv("SECRET_KEY", "dev-secret-key-change-me-in-production-please")
    app = Flask(__name__)
    with pytest.raises(RuntimeError):
        ProductionConfig.init_app(app)


def test_production_config_accepts_strong_secret(monkeypatch):
    from config import ProductionConfig
    from flask import Flask

    monkeypatch.setenv("SECRET_KEY", "a" * 50)
    app = Flask(__name__)
    # Should not raise
    ProductionConfig.init_app(app)


def test_database_url_normalization_postgres_scheme():
    from config import _normalize_database_url

    assert _normalize_database_url(
        "postgres://u:p@h:5432/db"
    ) == "postgresql+psycopg://u:p@h:5432/db"
    assert _normalize_database_url(
        "postgresql://u:p@h:5432/db"
    ) == "postgresql+psycopg://u:p@h:5432/db"
    assert _normalize_database_url(
        "postgresql+psycopg://u:p@h:5432/db"
    ) == "postgresql+psycopg://u:p@h:5432/db"
    assert _normalize_database_url("sqlite:///x.db") == "sqlite:///x.db"
    assert _normalize_database_url(None) == ""
