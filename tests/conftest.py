"""Pytest fixtures for FitControl Pro 2.0 tests."""
import os
import sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from models import db
from models.user import User


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user(app):
    with app.app_context():
        u = User(nome="Coach Teste", email="coach@test.com")
        u.set_password("Senha@1234")
        db.session.add(u)
        db.session.commit()
        return db.session.get(User, u.id)


@pytest.fixture()
def auth_client(client, user):
    client.post(
        "/auth/login",
        data={"email": user.email, "password": "Senha@1234"},
        follow_redirects=True,
    )
    return client
