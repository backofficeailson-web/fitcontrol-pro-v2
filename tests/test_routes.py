"""Smoke tests for protected routes."""


def test_dashboard_loads(auth_client):
    r = auth_client.get("/")
    assert r.status_code == 200
    assert b"FitControl" in r.data


def test_alunos_index(auth_client):
    r = auth_client.get("/alunos/")
    assert r.status_code == 200


def test_avaliacoes_index(auth_client):
    r = auth_client.get("/avaliacoes/")
    assert r.status_code == 200


def test_treinos_index(auth_client):
    r = auth_client.get("/treinos/")
    assert r.status_code == 200


def test_protocolos_index(auth_client):
    r = auth_client.get("/protocolos/")
    assert r.status_code == 200
    assert b"Pollock" in r.data
    assert b"Hipertrofia" in r.data


def test_relatorios_index(auth_client):
    r = auth_client.get("/relatorios/")
    assert r.status_code == 200


def test_api_protocolos_json(auth_client):
    r = auth_client.get("/api/protocolos")
    assert r.status_code == 200
    payload = r.get_json()
    assert "treino" in payload and "avaliacao" in payload
    assert any(p["chave"] == "pollock_3" for p in payload["avaliacao"])
