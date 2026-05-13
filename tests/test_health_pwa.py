"""Tests for health, readiness and PWA endpoints."""


def test_healthz_returns_ok(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    payload = r.get_json()
    assert payload["status"] == "ok"
    assert payload["service"] == "FitControl Pro"
    assert "version" in payload


def test_readyz_returns_ready(client):
    r = client.get("/readyz")
    assert r.status_code == 200
    payload = r.get_json()
    assert payload["status"] == "ready"
    assert payload["database"] == "ok"


def test_manifest_json(client):
    r = client.get("/manifest.json")
    assert r.status_code == 200
    payload = r.get_json()
    assert payload["name"] == "FitControl Pro"
    assert payload["short_name"] == "FitControl"
    assert payload["start_url"] == "/"
    assert payload["display"] == "standalone"
    assert payload["theme_color"] == "#050912"
    assert len(payload["icons"]) >= 2
    sizes = {icon["sizes"] for icon in payload["icons"]}
    assert "192x192" in sizes
    assert "512x512" in sizes


def test_service_worker_served(client):
    r = client.get("/service-worker.js")
    assert r.status_code == 200
    assert "javascript" in r.headers["Content-Type"]
    assert r.headers.get("Service-Worker-Allowed") == "/"
    assert b"fitcontrol" in r.data.lower()


def test_offline_page(client):
    r = client.get("/offline")
    assert r.status_code == 200
    assert b"offline" in r.data.lower() or b"Offline" in r.data
