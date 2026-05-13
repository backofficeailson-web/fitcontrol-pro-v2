"""Alunos CRUD tests."""
from models import db
from models.aluno import Aluno


def test_aluno_list_empty(auth_client):
    r = auth_client.get("/alunos/")
    assert r.status_code == 200
    assert b"Nenhum aluno" in r.data or b"Cadastrar aluno" in r.data


def test_aluno_create(auth_client, app, user):
    r = auth_client.post(
        "/alunos/novo",
        data={
            "nome": "Pedro Silva",
            "email": "pedro@test.com",
            "telefone": "11 99999-0000",
            "sexo": "masculino",
            "altura": "1.78",
            "peso_inicial": "82",
            "objetivo": "hipertrofia",
            "nivel_condicionamento": "iniciante",
            "status": "ativo",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    with app.app_context():
        aluno = db.session.query(Aluno).filter_by(nome="Pedro Silva", user_id=user.id).first()
        assert aluno is not None
        assert aluno.objetivo == "hipertrofia"


def test_aluno_isolation_between_users(client, app):
    """Garantir que um usuário não acessa alunos de outro."""
    from models.user import User
    with app.app_context():
        u1 = User(nome="Coach 1", email="c1@test.com"); u1.set_password("Senha@1234")
        u2 = User(nome="Coach 2", email="c2@test.com"); u2.set_password("Senha@1234")
        db.session.add_all([u1, u2]); db.session.commit()
        a = Aluno(user_id=u1.id, nome="Aluno do Coach 1", status="ativo",
                  nivel_condicionamento="iniciante")
        db.session.add(a); db.session.commit()
        aluno_id = a.id

    client.post("/auth/login", data={"email": "c2@test.com", "password": "Senha@1234"},
                follow_redirects=True)
    r = client.get(f"/alunos/{aluno_id}")
    assert r.status_code in (403, 404)
