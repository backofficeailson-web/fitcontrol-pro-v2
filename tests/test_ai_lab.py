"""Tests for the AI Lab module (file analysis)."""
import io
import zipfile

from models import db
from models.ai_analysis import AIAnalysis


def test_ai_lab_index_loads(auth_client):
    r = auth_client.get("/ai/")
    assert r.status_code == 200
    assert b"IA Lab" in r.data or b"An\xc3\xa1lise" in r.data


def test_ai_lab_upload_text_file(auth_client, app, user):
    data = {
        "arquivo": (io.BytesIO(b"print('hello world')\n# TODO: refactor\n"), "test.py"),
    }
    r = auth_client.post("/ai/upload", data=data,
                         content_type="multipart/form-data",
                         follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        a = db.session.query(AIAnalysis).filter_by(user_id=user.id).first()
        assert a is not None
        assert a.tipo_arquivo == "code"
        assert a.status == "done"
        assert a.score_seguranca is not None


def test_ai_lab_upload_zip(auth_client, app, user):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("app.py", "import flask\napp = flask.Flask(__name__)\n")
        zf.writestr("requirements.txt", "flask==3.0.3\n")
    buf.seek(0)
    data = {"arquivo": (buf, "projeto.zip")}
    r = auth_client.post("/ai/upload", data=data,
                         content_type="multipart/form-data",
                         follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        a = db.session.query(AIAnalysis).filter_by(user_id=user.id,
                                                   nome_arquivo="projeto.zip").first()
        assert a is not None
        assert a.tipo_arquivo == "zip"
        assert a.status == "done"
        assert a.relatorio_tecnico is not None


def test_ai_lab_upload_rejects_invalid_extension(auth_client):
    data = {"arquivo": (io.BytesIO(b"binary"), "malware.exe")}
    r = auth_client.post("/ai/upload", data=data,
                         content_type="multipart/form-data",
                         follow_redirects=True)
    assert r.status_code == 200
    # Should flash error and redirect back to index
    assert b"Upload inv" in r.data or b"inv\xc3\xa1lido" in r.data or b"n\xc3\xa3o permitida" in r.data


def test_ai_lab_status_json(auth_client, app, user):
    # Create analysis directly
    data = {"arquivo": (io.BytesIO(b"hello"), "doc.txt")}
    auth_client.post("/ai/upload", data=data,
                     content_type="multipart/form-data",
                     follow_redirects=True)
    with app.app_context():
        a = db.session.query(AIAnalysis).filter_by(user_id=user.id).first()
        aid = a.id
    r = auth_client.get(f"/ai/{aid}/status")
    assert r.status_code == 200
    payload = r.get_json()
    assert payload["id"] == aid
    assert "status" in payload
    assert "progresso" in payload


def test_ai_engine_detect_type():
    from services.ai_engine_analysis import AIAnalysisEngine
    assert AIAnalysisEngine.detect_type("x.zip", "application/zip") == "zip"
    assert AIAnalysisEngine.detect_type("x.pdf", "application/pdf") == "pdf"
    assert AIAnalysisEngine.detect_type("x.png", "image/png") == "image"
    assert AIAnalysisEngine.detect_type("x.py", "text/x-python") == "code"
    assert AIAnalysisEngine.detect_type("x.docx", "application/x") == "doc"
    assert AIAnalysisEngine.detect_type("x.md", "text/markdown") == "doc"
