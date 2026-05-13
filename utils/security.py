"""Security and ownership utilities."""
import re
from functools import wraps

from flask import abort
from flask_login import current_user

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_DANGEROUS_RE = re.compile(r"(javascript:|data:|vbscript:)", re.IGNORECASE)


def sanitize_text(value: str | None, max_length: int = 5000) -> str | None:
    if value is None:
        return None
    cleaned = _HTML_TAG_RE.sub("", str(value))
    cleaned = _DANGEROUS_RE.sub("", cleaned).strip()
    return cleaned[:max_length] if cleaned else None


def ensure_owner(entity, user_id: int):
    if entity is None:
        abort(404)
    owner_id = getattr(entity, "user_id", None)
    if owner_id != user_id:
        abort(403)
    return entity


def owner_required(loader):
    """Decorator factory that enforces ownership using a loader callable.

    Loader receives (id, user_id) and must return the entity or None.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            entity_id = kwargs.get("entity_id") or kwargs.get("id")
            entity = loader(entity_id, current_user.id)
            if entity is None:
                abort(404)
            return func(entity=entity, *args, **kwargs)
        return wrapper
    return decorator
