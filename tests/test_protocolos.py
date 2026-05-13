"""Protocolos catalog tests."""
from services.protocolo_service import ProtocoloService


def test_list_avaliacao_includes_pollock():
    chaves = [p.chave for p in ProtocoloService.list_avaliacao()]
    assert "pollock_3" in chaves
    assert "pollock_7" in chaves
    assert "imc" in chaves
    assert "rcq" in chaves


def test_list_treino_includes_required():
    chaves = [p.chave for p in ProtocoloService.list_treino()]
    for required in [
        "hipertrofia_iniciante", "hipertrofia_avancada", "emagrecimento",
        "condicionamento", "forca", "periodizacao", "full_body", "abc",
        "abcde", "upper_lower", "adaptacao_neural", "resistencia_muscular",
        "powerlifting", "bodybuilder", "gestantes", "beach_tenis",
        "futebol", "lipedema", "diabetes", "cardiacos",
    ]:
        assert required in chaves, f"Faltando protocolo: {required}"


def test_protocolo_especiais_tem_alerta():
    for chave in ["gestantes", "cardiacos", "diabetes", "lipedema"]:
        p = ProtocoloService.get(chave)
        assert p is not None
        assert p.requer_individualizacao is True
        assert p.alerta_medico
        assert ProtocoloService.is_especial(chave) is True


def test_protocolo_inexistente():
    assert ProtocoloService.get("inexistente") is None
