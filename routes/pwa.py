"""PWA endpoints: manifest, service worker, offline fallback.

The service-worker.js is served from the site root (`/service-worker.js`)
so it can control the whole scope. The manifest.json is served from
`/manifest.json` for the same reason and to keep iOS happy.
"""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, send_from_directory

pwa_bp = Blueprint("pwa", __name__)


@pwa_bp.route("/manifest.json")
def manifest():
    """Web App Manifest — controls installability and theming on Android/Chrome."""
    return jsonify(
        {
            "name": "FitControl Pro",
            "short_name": "FitControl",
            "description": "Plataforma SaaS Fitness premium — since 2018 Ailson Soares.",
            "lang": "pt-BR",
            "dir": "ltr",
            "start_url": "/",
            "scope": "/",
            "display": "standalone",
            "orientation": "portrait-primary",
            "background_color": "#050912",
            "theme_color": "#050912",
            "categories": ["fitness", "health", "productivity"],
            "icons": [
                {
                    "src": "/static/img/icons/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/static/img/icons/icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
            ],
        }
    )


@pwa_bp.route("/service-worker.js")
def service_worker():
    """Serve service-worker from root so its scope covers the whole site."""
    response = send_from_directory(
        current_app.static_folder, "js/service-worker.js", mimetype="application/javascript"
    )
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response


@pwa_bp.route("/offline")
def offline():
    """Offline fallback page rendered by the service worker."""
    return render_template("errors/offline.html"), 200
