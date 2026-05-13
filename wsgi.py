"""WSGI entrypoint for FitControl Pro 2.0.

Used by gunicorn in production:

    gunicorn wsgi:app
"""
import os

from app import create_app

# Default to production when launched via gunicorn / cloud platform
application = create_app(os.getenv("FLASK_ENV", "production"))
app = application
