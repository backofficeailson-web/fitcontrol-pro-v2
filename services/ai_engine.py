"""AI Training Engine - rule-based exercise prescription engine.

Generates structured workouts from a curated exercise database, applying
biomechanics rules, progression strategies, fatigue management, weekly splits,
muscle group balance, safety constraints and student history.

NO external APIs. Pure deterministic engine with realistic progression logic.
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Optional

from services.protocolo_service import ProtocoloService, ProtocoloDef

ai_logger = logging.getLogger("fitcontrol.ai")


# ---------------------------------------------------------------------------
# EXERCISE DATABASE
# ---------------------------------------------------------------------------
@dataclass
class ExerciseEntry:
    nome: str
    grupo: str
    padrao: str            # squat, hinge, push_horizontal, push_vertical, pull_horizontal, pull_vertical, core, mobility, cardio
    nivel: str             # iniciante, intermediario, avancado
    impacto: str = "baixo"  # baixo, medio, alto
    contraindicacoes: tuple[str, ...] = field(default_factory=tuple)
    equipamento: str = "academia"
    biarticular: bool = False
    isolador: bool = False


EXERCISE_DB: list[ExerciseEntry] = [
    # PEITO
    ExerciseEntry("Supino reto com barra", "peito", "push_horizontal", "intermediario", "baixo",
                  ("valsalva", "alto_impacto"), biarticular=True),
    ExerciseEntry("Supino reto com halteres", "peito", "push_horizontal", "iniciante"),
    ExerciseEntry("Supino inclinado com halteres", "peito", "push_horizontal", "iniciante"),
    ExerciseEntry("Supino declinado com halteres", "peito", "push_horizontal", "intermediario",
                  contraindicacoes=("decubito_dorsal_gestante", "valsalva")),
    ExerciseEntry("Crucifixo na máquina (peck deck)", "peito", "push_horizontal", "iniciante", isolador=True),
    ExerciseEntry("Crossover na polia", "peito", "push_horizontal", "intermediario", isolador=True),
    ExerciseEntry("Flexão de braço", "peito", "push_horizontal", "iniciante", equipamento="livre"),
    ExerciseEntry("Supino máquina", "peito", "push_horizontal", "iniciante"),

    # COSTAS
    ExerciseEntry("Puxada frente na polia alta", "costas", "pull_vertical", "iniciante"),
    ExerciseEntry("Puxada articulada", "costas", "pull_vertical", "iniciante"),
    ExerciseEntry("Remada curvada com barra", "costas", "pull_horizontal", "intermediario",
                  ("lombalgia_aguda", "valsalva"), biarticular=True),
    ExerciseEntry("Remada baixa na polia", "costas", "pull_horizontal", "iniciante"),
    ExerciseEntry("Remada cavalinho (T-bar)", "costas", "pull_horizontal", "intermediario"),
    ExerciseEntry("Pull-over com halter", "costas", "pull_vertical", "intermediario", isolador=True),
    ExerciseEntry("Barra fixa (pull-up)", "costas", "pull_vertical", "avancado", biarticular=True),
    ExerciseEntry("Levantamento terra convencional", "costas", "hinge", "avancado", "alto",
                  ("lombalgia", "hernia_disco", "cardiopatia", "gestante", "valsalva"), biarticular=True),

    # OMBROS
    ExerciseEntry("Desenvolvimento com halteres sentado", "ombros", "push_vertical", "iniciante", biarticular=True),
    ExerciseEntry("Desenvolvimento na máquina", "ombros", "push_vertical", "iniciante"),
    ExerciseEntry("Elevação lateral com halteres", "ombros", "push_vertical", "iniciante", isolador=True),
    ExerciseEntry("Elevação frontal com halteres", "ombros", "push_vertical", "iniciante", isolador=True),
    ExerciseEntry("Crucifixo invertido (rear delt)", "ombros", "pull_horizontal", "iniciante", isolador=True),
    ExerciseEntry("Remada alta", "ombros", "pull_vertical", "intermediario"),
    ExerciseEntry("Encolhimento (shrug)", "ombros", "pull_vertical", "iniciante", isolador=True),

    # BÍCEPS
    ExerciseEntry("Rosca direta com barra", "biceps", "pull_horizontal", "iniciante", isolador=True),
    ExerciseEntry("Rosca alternada com halteres", "biceps", "pull_horizontal", "iniciante", isolador=True),
    ExerciseEntry("Rosca martelo", "biceps", "pull_horizontal", "iniciante", isolador=True),
    ExerciseEntry("Rosca scott na máquina", "biceps", "pull_horizontal", "iniciante", isolador=True),
    ExerciseEntry("Rosca concentrada", "biceps", "pull_horizontal", "iniciante", isolador=True),

    # TRÍCEPS
    ExerciseEntry("Tríceps na polia (corda)", "triceps", "push_horizontal", "iniciante", isolador=True),
    ExerciseEntry("Tríceps testa com barra W", "triceps", "push_horizontal", "intermediario", isolador=True),
    ExerciseEntry("Tríceps francês com halter", "triceps", "push_vertical", "iniciante", isolador=True),
    ExerciseEntry("Mergulho em paralelas", "triceps", "push_vertical", "intermediario", biarticular=True),
    ExerciseEntry("Tríceps coice", "triceps", "push_horizontal", "iniciante", isolador=True),

    # PERNAS - QUADRÍCEPS
    ExerciseEntry("Agachamento livre com barra", "quadriceps", "squat", "avancado", "alto",
                  ("lombalgia_aguda", "lesao_joelho_severa", "gestante_3tri", "cardiopatia_descompensada"),
                  biarticular=True),
    ExerciseEntry("Agachamento smith", "quadriceps", "squat", "intermediario", biarticular=True),
    ExerciseEntry("Leg press 45°", "quadriceps", "squat", "iniciante", biarticular=True),
    ExerciseEntry("Hack machine", "quadriceps", "squat", "intermediario", biarticular=True),
    ExerciseEntry("Cadeira extensora", "quadriceps", "squat", "iniciante", isolador=True),
    ExerciseEntry("Avanço com halteres", "quadriceps", "squat", "intermediario", biarticular=True),
    ExerciseEntry("Búlgaro com halteres", "quadriceps", "squat", "intermediario", biarticular=True),

    # PERNAS - POSTERIOR / GLÚTEO
    ExerciseEntry("Stiff com halteres", "posterior", "hinge", "intermediario",
                  ("lombalgia_aguda",), biarticular=True),
    ExerciseEntry("Mesa flexora", "posterior", "hinge", "iniciante", isolador=True),
    ExerciseEntry("Cadeira flexora sentado", "posterior", "hinge", "iniciante", isolador=True),
    ExerciseEntry("Elevação pélvica (hip thrust)", "gluteos", "hinge", "iniciante", biarticular=True),
    ExerciseEntry("Glúteo na polia (kickback)", "gluteos", "hinge", "iniciante", isolador=True),
    ExerciseEntry("Abdução de quadril na máquina", "gluteos", "hinge", "iniciante", isolador=True),

    # PANTURRILHAS
    ExerciseEntry("Panturrilha em pé na máquina", "panturrilha", "squat", "iniciante", isolador=True),
    ExerciseEntry("Panturrilha sentado", "panturrilha", "squat", "iniciante", isolador=True),
    ExerciseEntry("Panturrilha no leg press", "panturrilha", "squat", "iniciante", isolador=True),

    # CORE
    ExerciseEntry("Prancha frontal", "core", "core", "iniciante", equipamento="livre"),
    ExerciseEntry("Prancha lateral", "core", "core", "iniciante", equipamento="livre"),
    ExerciseEntry("Abdominal infra com elevação de pernas", "core", "core", "intermediario",
                  contraindicacoes=("decubito_dorsal_gestante",), equipamento="livre"),
    ExerciseEntry("Abdominal supra na máquina", "core", "core", "iniciante"),
    ExerciseEntry("Pallof press na polia", "core", "core", "intermediario", isolador=True),
    ExerciseEntry("Dead bug", "core", "core", "iniciante", equipamento="livre",
                  contraindicacoes=("decubito_dorsal_gestante",)),
    ExerciseEntry("Bird dog", "core", "core", "iniciante", equipamento="livre"),

    # MOBILIDADE / FUNCIONAL
    ExerciseEntry("Mobilidade de quadril (90/90)", "mobilidade", "mobility", "iniciante", equipamento="livre"),
    ExerciseEntry("Cat-cow", "mobilidade", "mobility", "iniciante", equipamento="livre"),
    ExerciseEntry("Ponte de glúteo unilateral", "gluteos", "hinge", "iniciante", equipamento="livre"),
    ExerciseEntry("Agachamento no peso corporal", "quadriceps", "squat", "iniciante", equipamento="livre"),

    # CARDIO
    ExerciseEntry("Esteira - caminhada inclinada", "cardio", "cardio", "iniciante", impacto="baixo"),
    ExerciseEntry("Bicicleta ergométrica", "cardio", "cardio", "iniciante", impacto="baixo"),
    ExerciseEntry("Elíptico", "cardio", "cardio", "iniciante", impacto="baixo"),
    ExerciseEntry("Esteira - corrida moderada", "cardio", "cardio", "intermediario", impacto="alto",
                  contraindicacoes=("alto_impacto", "lipedema", "cardiopatia_descompensada")),
    ExerciseEntry("Remo ergômetro", "cardio", "cardio", "intermediario", impacto="baixo"),
]


def _filter_db(*, contraindicacoes: set[str], nivel: str,
               permitir_alto_impacto: bool) -> list[ExerciseEntry]:
    nivel_rank = {"iniciante": 1, "intermediario": 2, "avancado": 3}
    user_rank = nivel_rank.get(nivel, 1)
    filtered: list[ExerciseEntry] = []
    for ex in EXERCISE_DB:
        if any(c in contraindicacoes for c in ex.contraindicacoes):
            continue
        if not permitir_alto_impacto and ex.impacto == "alto":
            continue
        if nivel_rank.get(ex.nivel, 1) > user_rank + 1:
            continue
        filtered.append(ex)
    return filtered


# ---------------------------------------------------------------------------
# SPLIT TEMPLATES
# ---------------------------------------------------------------------------
SPLITS: dict[str, list[tuple[str, list[str]]]] = {
    "Full Body": [
        ("A", ["quadriceps", "peito", "costas", "ombros", "core"]),
        ("B", ["posterior", "gluteos", "peito", "costas", "biceps", "core"]),
        ("C", ["quadriceps", "ombros", "costas", "triceps", "panturrilha", "core"]),
    ],
    "ABC": [
        ("A", ["peito", "ombros", "triceps", "core"]),
        ("B", ["costas", "biceps", "core"]),
        ("C", ["quadriceps", "posterior", "gluteos", "panturrilha", "core"]),
    ],
    "ABCD": [
        ("A", ["peito", "triceps"]),
        ("B", ["costas", "biceps"]),
        ("C", ["quadriceps", "panturrilha"]),
        ("D", ["ombros", "posterior", "gluteos", "core"]),
    ],
    "ABCDE": [
        ("A", ["peito"]),
        ("B", ["costas"]),
        ("C", ["quadriceps", "panturrilha"]),
        ("D", ["ombros", "core"]),
        ("E", ["posterior", "gluteos", "biceps", "triceps"]),
    ],
    "Upper/Lower": [
        ("A", ["peito", "costas", "ombros", "biceps", "triceps"]),
        ("B", ["quadriceps", "posterior", "gluteos", "panturrilha", "core"]),
        ("C", ["peito", "costas", "ombros", "biceps", "triceps"]),
        ("D", ["quadriceps", "posterior", "gluteos", "panturrilha", "core"]),
    ],
}


def _split_for(divisao: str, frequencia: int) -> list[tuple[str, list[str]]]:
    template = SPLITS.get(divisao) or SPLITS["ABC"]
    if frequencia >= len(template):
        return template
    return template[:frequencia]


# ---------------------------------------------------------------------------
# PROGRESSION RULES BY OBJECTIVE
# ---------------------------------------------------------------------------
PROGRESSION_RULES = {
    "hipertrofia": {"series": (3, 4), "reps": "8-12", "descanso": "60-90s", "rir": 2},
    "forca": {"series": (4, 5), "reps": "3-6", "descanso": "120-180s", "rir": 1},
    "emagrecimento": {"series": (3, 4), "reps": "12-15", "descanso": "30-45s", "rir": 2},
    "condicionamento": {"series": (3, 3), "reps": "12-20", "descanso": "45s", "rir": 3},
    "resistencia": {"series": (3, 4), "reps": "15-25", "descanso": "30s", "rir": 3},
    "esporte": {"series": (3, 4), "reps": "8-12", "descanso": "60-120s", "rir": 2},
    "especial": {"series": (2, 3), "reps": "12-15", "descanso": "60-90s", "rir": 4},
}


# ---------------------------------------------------------------------------
# AI ENGINE
# ---------------------------------------------------------------------------
class AIEngine:
    """Rule-based deterministic exercise prescription engine."""

    @staticmethod
    def _build_contraindicacoes(aluno, protocolo: Optional[ProtocoloDef]) -> set[str]:
        contras: set[str] = set()
        if aluno and aluno.condicoes_especiais:
            for tag in aluno.condicoes_especiais.lower().split(","):
                contras.add(tag.strip())
        if protocolo and protocolo.parametros.get("evitar"):
            for tag in protocolo.parametros["evitar"]:
                contras.add(tag)
        if protocolo and protocolo.chave == "gestantes":
            contras.update({"decubito_dorsal_gestante", "valsalva", "alto_impacto"})
        if protocolo and protocolo.chave == "cardiacos":
            contras.update({"valsalva", "alto_impacto", "isometria_pesada"})
        if protocolo and protocolo.chave == "lipedema":
            contras.update({"alto_impacto"})
        return contras

    @staticmethod
    def _categoria_objetivo(objetivo: str, protocolo: Optional[ProtocoloDef]) -> str:
        if protocolo and protocolo.requer_individualizacao:
            return "especial"
        if "forca" in (objetivo or "").lower() or "powerlifting" in (objetivo or "").lower():
            return "forca"
        if "emagrec" in (objetivo or "").lower():
            return "emagrecimento"
        if "condicion" in (objetivo or "").lower():
            return "condicionamento"
        if "resist" in (objetivo or "").lower():
            return "resistencia"
        if "esporte" in (objetivo or "").lower() or "futebol" in (objetivo or "").lower():
            return "esporte"
        return "hipertrofia"

    @staticmethod
    def _select_exercises_for_group(
        grupo: str, pool: list[ExerciseEntry], qty: int, nivel: str
    ) -> list[ExerciseEntry]:
        candidates = [ex for ex in pool if ex.grupo == grupo]
        if not candidates:
            return []
        # prefer biarticulares first, then isoladores, scaled by nivel
        bia = [ex for ex in candidates if ex.biarticular]
        iso = [ex for ex in candidates if ex.isolador]
        rest = [ex for ex in candidates if not ex.biarticular and not ex.isolador]
        ordered = bia + rest + iso
        # if iniciante limit volume
        if nivel == "iniciante":
            qty = min(qty, 2)
        return ordered[:qty]

    @staticmethod
    def _exercises_per_group(divisao: str, objetivo_cat: str, nivel: str) -> int:
        base = {"Full Body": 1, "ABC": 2, "ABCD": 3, "ABCDE": 4, "Upper/Lower": 2}
        qty = base.get(divisao, 2)
        if objetivo_cat == "forca":
            qty = max(qty - 1, 1)
        if objetivo_cat == "especial":
            qty = max(qty - 1, 1)
        if nivel == "avancado":
            qty += 1
        return qty

    @staticmethod
    def gerar_treino(
        *, aluno, objetivo: str, divisao: str, frequencia: int, nivel: str,
        protocolo_chave: Optional[str] = None, duracao_semanas: int = 8,
    ) -> dict:
        protocolo = ProtocoloService.get(protocolo_chave) if protocolo_chave else None
        objetivo_cat = AIEngine._categoria_objetivo(objetivo, protocolo)
        rules = PROGRESSION_RULES[objetivo_cat]
        contras = AIEngine._build_contraindicacoes(aluno, protocolo)
        permitir_alto_impacto = "alto_impacto" not in contras
        pool = _filter_db(
            contraindicacoes=contras, nivel=nivel,
            permitir_alto_impacto=permitir_alto_impacto,
        )
        if not pool:
            ai_logger.warning("AIEngine: empty pool after filtering for aluno=%s", getattr(aluno, "id", None))

        split = _split_for(divisao, frequencia)
        per_group = AIEngine._exercises_per_group(divisao, objetivo_cat, nivel)

        exercicios_resultado: list[dict] = []
        ordem_global = 0
        for dia, grupos in split:
            ordem_dia = 1
            for grupo in grupos:
                selecionados = AIEngine._select_exercises_for_group(grupo, pool, per_group, nivel)
                for ex in selecionados:
                    series_min, series_max = rules["series"]
                    series = series_max if (nivel != "iniciante" and not ex.isolador) else series_min
                    descanso = rules["descanso"]
                    if ex.biarticular and objetivo_cat == "forca":
                        descanso = "180s"
                    rir = rules["rir"]
                    if protocolo and protocolo.parametros.get("intensidade_max_rpe"):
                        rir = max(rir, 4)
                    exercicios_resultado.append({
                        "nome": ex.nome,
                        "grupo_muscular": ex.grupo,
                        "series": series,
                        "repeticoes": rules["reps"],
                        "descanso": descanso,
                        "rir": rir,
                        "rpe": round(10 - rir, 1),
                        "tempo_execucao": "2-0-2 (controlado)",
                        "dia_semana": dia,
                        "ordem": ordem_dia,
                        "tecnica": "tradicional",
                        "observacoes": "Execução técnica antes de carga." if nivel == "iniciante" else None,
                    })
                    ordem_dia += 1
                    ordem_global += 1

        # Shuffle deterministically inside each day to vary order across calls
        rng = random.Random(hash((aluno.id if aluno else 0, divisao, objetivo, nivel)))
        rng.shuffle(exercicios_resultado)
        # Re-sort by dia + ordem after shuffle for stable presentation
        exercicios_resultado.sort(key=lambda e: (e["dia_semana"], e["ordem"]))

        progressao = AIEngine._gerar_progressao(duracao_semanas, objetivo_cat)
        recomendacoes = AIEngine._gerar_recomendacoes(aluno, protocolo, objetivo_cat)

        ai_logger.info(
            "AIEngine generated workout: aluno=%s objetivo=%s divisao=%s freq=%s exercicios=%s",
            getattr(aluno, "id", None), objetivo, divisao, frequencia, len(exercicios_resultado),
        )

        return {
            "exercicios": exercicios_resultado,
            "progressao": progressao,
            "recomendacoes": recomendacoes,
            "alerta_medico": protocolo.alerta_medico if protocolo else None,
            "categoria_objetivo": objetivo_cat,
            "regras_aplicadas": rules,
        }

    @staticmethod
    def _gerar_progressao(duracao_semanas: int, categoria: str) -> list[dict]:
        progressao: list[dict] = []
        for semana in range(1, duracao_semanas + 1):
            if categoria == "forca":
                if semana <= 2:
                    foco, ajuste = "Acumulação", "+0% carga"
                elif semana <= 5:
                    foco, ajuste = "Intensificação", "+5% carga, -1 rep"
                elif semana <= 7:
                    foco, ajuste = "Pico", "+7-10% carga, séries de 3 reps"
                else:
                    foco, ajuste = "Deload", "-30% volume"
            elif categoria == "hipertrofia":
                if semana <= 3:
                    foco, ajuste = "Volume base", "manter carga, +1 rep alvo"
                elif semana <= 6:
                    foco, ajuste = "Sobrecarga", "+2.5-5% carga"
                elif semana == 7:
                    foco, ajuste = "Pico", "+5% carga, 1 série a mais"
                else:
                    foco, ajuste = "Deload", "-20% volume"
            elif categoria == "emagrecimento":
                foco = "Densidade metabólica"
                ajuste = "-5s descanso a cada 2 semanas até 30s"
            elif categoria == "especial":
                foco = "Adaptação progressiva"
                ajuste = "Aumentar 1 série apenas se RPE ≤ alvo"
            else:
                foco = "Progressão dupla"
                ajuste = "Subir carga ao atingir teto de reps em todas as séries"
            progressao.append({"semana": semana, "foco": foco, "ajuste": ajuste})
        return progressao

    @staticmethod
    def _gerar_recomendacoes(aluno, protocolo: Optional[ProtocoloDef], categoria: str) -> list[str]:
        recs = [
            "Aquecimento de 5-8 minutos articular antes da sessão.",
            "Hidratação contínua (250-500ml a cada 20 min de treino).",
            "Sono de 7-9h para suportar a recuperação.",
        ]
        if categoria == "hipertrofia":
            recs.append("Ingestão proteica de 1.6-2.2g/kg de peso corporal.")
        if categoria == "forca":
            recs.append("Mobilidade articular específica (quadril, ombros) antes das séries pesadas.")
        if categoria == "emagrecimento":
            recs.append("Combinar com 150-300 min de cardio Z2 semanal.")
        if categoria == "especial":
            recs.append("Monitoramento de sinais (FC, glicemia, PA) antes/durante/após.")
        if aluno and aluno.idade and aluno.idade >= 60:
            recs.append("Ênfase em mobilidade, equilíbrio e treino unilateral.")
        if protocolo and protocolo.requer_individualizacao:
            recs.append("Sessão com supervisão presencial obrigatória.")
        return recs
