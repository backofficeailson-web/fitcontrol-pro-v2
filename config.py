"""
FitControl Pro 2.0 - Configuration Module
Premium SaaS Fitness Platform — Production / Cloud Ready
since 2018 Ailson Soares
"""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
LOG_DIR = BASE_DIR / "logs"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"

# Garantia forte para Windows/Linux/Docker: cria as pastas no import do config
# para evitar falha quando o SQLite tenta abrir o arquivo antes do app factory.
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Load .env in dev (production platforms inject env vars directly)
load_dotenv(BASE_DIR / ".env")


def _default_sqlite_url() -> str:
    """Return an absolute SQLite URL compatible with Windows and Unix.

    SQLAlchemy expects absolute SQLite paths in URL form like:
      sqlite:///C:/path/to/db.sqlite   (Windows)
      sqlite:////home/user/db.sqlite   (Unix)
    Using Path.resolve().as_posix() avoids backslash/relative-path issues.
    """
    db_path = (INSTANCE_DIR / "fitcontrol.db").resolve().as_posix()
    return f"sqlite:///{db_path}"


print(f"[*] Pasta instance pronta: {INSTANCE_DIR}")
print(f"[*] Banco SQLite local padrão: {_default_sqlite_url()}")




def _normalize_database_url(url: str | None) -> str:
    """
    Normalize DATABASE_URL.

    - Render/Railway/Heroku-style 'postgres://' is converted to 'postgresql+psycopg://'.
    - 'postgresql://' is upgraded to 'postgresql+psycopg://' so the modern psycopg3 driver is used.
    - SQLite/other URLs are returned unchanged.
    """
    if not url:
        return ""
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    """Base configuration shared across environments."""

    # ---------- App identity ----------
    APP_NAME = "FitControl Pro"
    APP_VERSION = "2.0.0"
    APP_TAGLINE = "since 2018 Ailson Soares"

    # ---------- Paths ----------
    BASE_DIR = BASE_DIR
    INSTANCE_DIR = INSTANCE_DIR
    LOG_DIR = LOG_DIR
    UPLOAD_DIR = UPLOAD_DIR

    # ---------- Secrets ----------
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me-in-production-please")
    WTF_CSRF_SECRET_KEY = os.getenv("WTF_CSRF_SECRET_KEY", SECRET_KEY)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ---------- Database ----------
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv("DATABASE_URL")) or _default_sqlite_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # ---------- Session / Cookies ----------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", False)
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8  # 8h

    # ---------- Uploads ----------
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))
    UPLOAD_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}

    # ---------- Rate limit ----------
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per hour")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_ENABLED = True

    # ---------- Logging ----------
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_STDOUT = _env_bool("LOG_TO_STDOUT", False)

    # ---------- Proxy (Render / Railway / Fly / Heroku put us behind reverse proxy) ----------
    BEHIND_PROXY = _env_bool("BEHIND_PROXY", False)

    # ---------- Security headers / CSP ----------
    ENABLE_SECURITY_HEADERS = True
    # Fonts/styles use Google CDN and Chart.js comes from jsdelivr
    CONTENT_SECURITY_POLICY = (
        "default-src 'self'; "
        "img-src 'self' data: blob:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    @classmethod
    def init_app(cls, app):
        cls.INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    SESSION_COOKIE_SECURE = False
    ENABLE_SECURITY_HEADERS = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    BEHIND_PROXY = True
    LOG_TO_STDOUT = True

    @classmethod
    def init_app(cls, app):
        super().init_app(app)

        # ---- Mandatory production validation ----
        weak_keys = {
            "",
            "dev-secret-key-change-me-in-production-please",
            "change-this-to-a-very-long-random-secret-key-in-production",
        }
        secret = (os.getenv("SECRET_KEY") or "").strip()
        if not secret or secret in weak_keys or len(secret) < 24:
            raise RuntimeError(
                "FitControl Pro: SECRET_KEY ausente ou fraco em produção. "
                "Defina SECRET_KEY com pelo menos 24 caracteres aleatórios."
            )

        db_url = os.getenv("DATABASE_URL", "").strip()
        if not db_url:
            app.logger.warning(
                "DATABASE_URL não definido em produção — usando SQLite local "
                "(NÃO RECOMENDADO). Defina DATABASE_URL para PostgreSQL."
            )
        elif db_url.startswith("sqlite"):
            app.logger.warning(
                "Produção usando SQLite. Recomendado migrar para PostgreSQL "
                "via variável DATABASE_URL."
            )


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(name: str | None = None):
    name = (name or os.getenv("FLASK_ENV", "development")).lower()
    return CONFIG_MAP.get(name, DevelopmentConfig)
