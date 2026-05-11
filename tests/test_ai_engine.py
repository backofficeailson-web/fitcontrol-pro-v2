"""AI Engine tests."""
from datetime import date

from services.ai_engine import AIEngine


class FakeAluno:
    def __init__(self, **kw):
        self.id = kw.get("id", 1)
        self.idade = kw.get("idade", 28)
        self.sexo = kw.get("sexo", "masculino")
        self.condicoes_especiais = kw.get("condicoes_especiais", None)
        self.nivel_condicionamento = kw.get("nivel_condicionamento", "iniciante")
        self.altura = kw.get("altura", 1.78)


def test_ai_engine_generates_workout_iniciante():
    aluno = FakeAluno()
    plano = AIEngine.gerar_treino(
        aluno=aluno, objetivo="hipertrofia", divisao="ABC",
        frequencia=3, nivel="iniciante",
    )
    assert "exercicios" in plano
    assert len(plano["exercicios"]) > 0
    assert "progressao" in plano
    assert len(plano["progressao"]) == 8
    assert plano["categoria_objetivo"] == "hipertrofia"


def test_ai_engine_blocks_high_impact_for_gestante():
    aluno = FakeAluno(condicoes_especiais="gestante")
    plano = AIEngine.gerar_treino(
        aluno=aluno, objetivo="condicionamento", divisao="Full Body",
        frequencia=3, nivel="iniciante", protocolo_chave="gestantes",
    )
    nomes = [e["nome"].lower() for e in plano["exercicios"]]
    assert all("levantamento terra" not in n for n in nomes)
    assert plano["alerta_medico"] is not None


def test_ai_engine_cardiacos_alerta():
    aluno = FakeAluno(condicoes_especiais="cardiopatia")
    plano = AIEngine.gerar_treino(
        aluno=aluno, objetivo="condicionamento", divisao="Full Body",
        frequencia=3, nivel="iniciante", protocolo_chave="cardiacos",
    )
    assert plano["alerta_medico"] is not None
    nomes = [e["nome"].lower() for e in plano["exercicios"]]
    assert all("levantamento terra" not in n for n in nomes)


def test_ai_engine_progression_for_forca():
    aluno = FakeAluno(nivel_condicionamento="intermediario")
    plano = AIEngine.gerar_treino(
        aluno=aluno, objetivo="forca", divisao="Upper/Lower",
        frequencia=4, nivel="intermediario",
    )
    fases = [p["foco"] for p in plano["progressao"]]
    assert "Deload" in fases
    assert plano["categoria_objetivo"] == "forca"


def test_ai_engine_no_empty_exercises_for_normal_user():
    aluno = FakeAluno()
    plano = AIEngine.gerar_treino(
        aluno=aluno, objetivo="emagrecimento", divisao="Full Body",
        frequencia=4, nivel="iniciante",
    )
    assert len(plano["exercicios"]) >= 5
    for ex in plano["exercicios"]:
        assert ex["series"] >= 1
        assert ex["repeticoes"]
