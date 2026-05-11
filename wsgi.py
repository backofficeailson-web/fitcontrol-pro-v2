"""WSGI entrypoint for FitControl Pro 2.0."""
from app import create_app

application = create_app()
app = application
