"""Backward-compatible executable entrypoint for FitControl Pro V2."""
import os
from app import create_app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=flask_app.config.get("DEBUG", False),
    )
