"""Dashboard aggregation service — optimized for production.

Performance principles applied:
- COUNT/aggregates run in SQL (no Python loops over .all()).
- Time-series queries use GROUP BY in the database.
- Lists are bounded by LIMIT.
"""
from __future__ import annotations

from datetime import datetime, UTC, timedelta

from sqlalchemy import func

from models import db
from models.aluno import Aluno
from models.avaliacao import Avaliacao
from models.treino import Treino
from repositories.aluno_repository import AlunoRepository
from repositories.avaliacao_repository import AvaliacaoRepository
from repositories.treino_repository import TreinoRepository
from repositories.protocolo_repository import ProtocoloRepository
from repositories.log_repository import LogRepository


class DashboardService:
    # ---------------- Métricas (counts em SQL) ----------------
    @staticmethod
    def metrics(user_id: int) -> dict:
        return {
            "total_alunos": AlunoRepository.count_for_user(user_id),
            "alunos_ativos": AlunoRepository.count_active_for_user(user_id),
            "total_avaliacoes": AvaliacaoRepository.count_for_user(user_id),
            "total_treinos": TreinoRepository.count_for_user(user_id),
            "treinos_ativos": TreinoRepository.count_active_for_user(user_id),
            "protocolos_ativos": ProtocoloRepository.count_active_for_user(user_id),
        }

    # ---------------- Feed (LIMIT em SQL) ----------------
    @staticmethod
    def feed(user_id: int) -> dict:
        return {
            "ultimos_alunos": AlunoRepository.recent_for_user(user_id, limit=5),
            "ultimas_avaliacoes": AvaliacaoRepository.latest_for_user(user_id, limit=5),
            "ultimos_treinos": TreinoRepository.recent_for_user(user_id, limit=5),
            "logs": LogRepository.latest_for_user(user_id, limit=8),
        }

    # ---------------- Evolução (LIMIT + ORDER BY) ----------------
    @staticmethod
    def evolucao_chart(user_id: int) -> dict:
        avals = AvaliacaoRepository.latest_for_user(user_id, limit=12)
        avals = list(reversed(avals))
        return {
            "labels": [a.data.strftime("%d/%m") if a.data else "" for a in avals],
            "peso": [a.peso for a in avals],
            "gordura": [a.percentual_gordura for a in avals],
            "imc": [a.imc for a in avals],
        }

    # ---------------- Atividade da semana (GROUP BY em SQL) ----------------
    @staticmethod
    def atividade_semana(user_id: int) -> dict:
        hoje = datetime.now(UTC).date()
        inicio = hoje - timedelta(days=6)

        # Avaliações por dia: SELECT data, COUNT(*) ... GROUP BY data
        avals_by_day = dict(
            db.session.query(Avaliacao.data, func.count(Avaliacao.id))
            .filter(Avaliacao.user_id == user_id)
            .filter(Avaliacao.data >= inicio)
            .filter(Avaliacao.data <= hoje)
            .group_by(Avaliacao.data)
            .all()
        )

        # Treinos por dia (created_at é DATETIME → trunc to date)
        treinos_by_day_rows = (
            db.session.query(func.date(Treino.created_at), func.count(Treino.id))
            .filter(Treino.user_id == user_id)
            .filter(Treino.created_at >= datetime.combine(inicio, datetime.min.time()))
            .group_by(func.date(Treino.created_at))
            .all()
        )
        treinos_by_day = {}
        for raw_date, count in treinos_by_day_rows:
            if isinstance(raw_date, str):
                # SQLite returns 'YYYY-MM-DD'
                try:
                    raw_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
                except ValueError:
                    continue
            treinos_by_day[raw_date] = count

        labels, avaliacoes_serie, treinos_serie = [], [], []
        for i in range(7):
            dia = inicio + timedelta(days=i)
            labels.append(dia.strftime("%d/%m"))
            avaliacoes_serie.append(int(avals_by_day.get(dia, 0)))
            treinos_serie.append(int(treinos_by_day.get(dia, 0)))

        return {
            "labels": labels,
            "avaliacoes": avaliacoes_serie,
            "treinos": treinos_serie,
        }
