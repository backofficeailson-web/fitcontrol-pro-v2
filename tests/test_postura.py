"""Tests for the Postura (postural assessment) module."""
import io

from models import db
from models.aluno import Aluno
from models.postura import AvaliacaoPostural


def _create_aluno(app, user):
    with app.app_context():
        a = Aluno(user_id=user.id, nome="Aluno Teste", status="ativo",
                  nivel_condicionamento="iniciante")
        db.session.add(a)
        db.session.commit()
        return a.id


def test_postura_index_loads(auth_client):
    r = auth_client.get("/postura/")
    assert r.status_code == 200
    assert b"Avalia" in r.data


def test_postura_por_aluno(auth_client, app, user):
    aluno_id = _create_aluno(app, user)
    r = auth_client.get(f"/postura/aluno/{aluno_id}")
    assert r.status_code == 200


def test_postura_create_form_loads(auth_client, app, user):
    aluno_id = _create_aluno(app, user)
    r = auth_client.get(f"/postura/novo/{aluno_id}")
    assert r.status_code == 200
    assert b"Cab" in r.data  # "Cabeça"


def test_postura_create_persists(auth_client, app, user):
    aluno_id = _create_aluno(app, user)
    r = auth_client.post(
        f"/postura/novo/{aluno_id}",
        data={
            "data": "2026-05-01",
            "cabeca": "anteriorizada",
            "cervical": "retificada",
            "ombros": "elevado direito",
            "grau_desvio": "moderado",
            "dor_relatada": "cervical leve",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    with app.app_context():
        p = db.session.query(AvaliacaoPostural).filter_by(aluno_id=aluno_id).first()
        assert p is not None
        assert p.cabeca == "anteriorizada"
        assert p.grau_desvio == "moderado"


def test_postura_isolation_between_users(client, app):
    """Garantir isolamento entre usuários."""
    from models.user import User
    with app.app_context():
        u1 = User(nome="U1", email="u1@t.com"); u1.set_password("Senha@1234")
        u2 = User(nome="U2", email="u2@t.com"); u2.set_password("Senha@1234")
        db.session.add_all([u1, u2]); db.session.commit()
        a = Aluno(user_id=u1.id, nome="Aluno U1", status="ativo",
                  nivel_condicionamento="iniciante")
        db.session.add(a); db.session.commit()
        post = AvaliacaoPostural(user_id=u1.id, aluno_id=a.id, data=None,
                                 cabeca="x", grau_desvio="leve")
        from datetime import date
        post.data = date(2026, 5, 1)
        db.session.add(post); db.session.commit()
        post_id = post.id

    client.post("/auth/login",
                data={"email": "u2@t.com", "password": "Senha@1234"},
                follow_redirects=True)
    r = client.get(f"/postura/{post_id}")
    assert r.status_code == 404
