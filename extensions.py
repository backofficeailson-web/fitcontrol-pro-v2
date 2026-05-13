"""Shared Flask extensions - imported by app factory and blueprints.

Keeping extensions in a dedicated module avoids circular imports
between routes/* and app.py.

The Limiter chooses Redis automatically when RATELIMIT_STORAGE_URI starts with
'redis://' (production), and falls back to in-memory storage when unset
(development / testing).
"""
import os

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

_storage_uri = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri,
    headers_enabled=True,
    default_limits=[os.getenv("RATELIMIT_DEFAULT", "200 per hour")],
)
