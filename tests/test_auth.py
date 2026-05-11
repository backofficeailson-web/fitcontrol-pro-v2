"""Authentication tests."""
from models import db
from models.user import User


def test_login_page_loads(client):
    r = client.get("/auth/login")
    assert r.status_code == 200
    assert b"FitControl" in r.data
    assert b"since 2018 Ailson Soares" in r.data


def test_register_creates_user(client, app):
    r = client.post(
        "/auth/register",
        data={
            "nome": "Novo Coach",
            "email": "novo@coach.com",
            "cref": "001-G/SP",
            "password": "Senha@1234",
            "confirm_password": "Senha@1234",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    with app.app_context():
        assert db.session.query(User).filter_by(email="novo@coach.com").first() is not None


def test_login_with_valid_credentials(client, user):
    r = client.post(
        "/auth/login",
        data={"email": user.email, "password": "Senha@1234"},
        follow_redirects=True,
    )
    assert r.status_code == 200


def test_login_with_invalid_credentials(client, user):
    r = client.post(
        "/auth/login",
        data={"email": user.email, "password": "errada"},
        follow_redirects=True,
    )
    assert b"Credenciais inv" in r.data or b"inv" in r.data.lower()


def test_dashboard_requires_login(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (301, 302)
    assert "/auth/login" in r.headers.get("Location", "")


def test_logout(auth_client):
    r = auth_client.get("/auth/logout", follow_redirects=False)
    assert r.status_code in (301, 302)
