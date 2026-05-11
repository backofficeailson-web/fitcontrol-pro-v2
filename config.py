"""
FitControl Pro V2 - production-ready configuration.
Premium SaaS Fitness Platform • since 2018 Ailson Soares
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _database_url() -> str:
    raw = os.getenv("DATABASE_URL", "").strip()
    if not raw:
        return f"sqlite:///{(BASE_DIR / 'instance' / 'fitcontrol.db').as_posix()}"
    if raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql+psycopg://", 1)
    elif raw.startswith("postgresql://") and "+" not in raw.split("://", 1)[0]:
        raw = raw.replace("postgresql://", "postgresql+psycopg://", 1)
    if raw.startswith("sqlite:///") and not raw.startswith("sqlite:////"):
        sqlite_path = raw.replace("sqlite:///", "", 1)
        if sqlite_path and not Path(sqlite_path).is_absolute():
            return f"sqlite:///{(BASE_DIR / sqlite_path).resolve().as_posix()}"
    return raw


def _engine_options(uri: str) -> dict:
    if uri.startswith("sqlite"):
        return {"pool_pre_ping": True, "connect_args": {"check_same_thread": False}}
    return {
        "pool_pre_ping": True,
        "pool_recycle": int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "280")),
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "10")),
    }


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me-in-production")
    WTF_CSRF_SECRET_KEY = os.getenv("WTF_CSRF_SECRET_KEY", SECRET_KEY)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = int(os.getenv("WTF_CSRF_TIME_LIMIT", "3600"))

    BASE_DIR = BASE_DIR
    INSTANCE_DIR = BASE_DIR / "instance"
    LOG_DIR = BASE_DIR / "logs"
    UPLOAD_DIR = BASE_DIR / "static" / "uploads"

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options(SQLALCHEMY_DATABASE_URI)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", False)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME", str(60 * 60 * 8)))

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))
    UPLOAD_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}

    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per hour")
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL") or os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    JSON_LOGS = _bool_env("JSON_LOGS", False)

    APP_NAME = "FitControl Pro"
    APP_VERSION = "2.1.0-enterprise"
    APP_TAGLINE = "since 2018 Ailson Soares"

    SECURITY_HEADERS_ENABLED = _bool_env("SECURITY_HEADERS_ENABLED", True)
    FORCE_HTTPS = _bool_env("FORCE_HTTPS", False)

    @classmethod
    def init_app(cls, app):
        cls.INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate_environment(cls) -> None:
        env = os.getenv("FLASK_ENV", "development")
        parsed = urlparse(cls.SQLALCHEMY_DATABASE_URI)
        if env == "production":
            if cls.SECRET_KEY.startswith("dev-") or "change-me" in cls.SECRET_KEY:
                raise RuntimeError("SECRET_KEY segura é obrigatória em produção.")
            if parsed.scheme.startswith("sqlite"):
                raise RuntimeError("PostgreSQL é obrigatório em produção. Configure DATABASE_URL.")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    FORCE_HTTPS = _bool_env("FORCE_HTTPS", True)


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(name: str | None = None):
    name = name or os.getenv("FLASK_ENV", "development")
    return CONFIG_MAP.get(name, DevelopmentConfig)
