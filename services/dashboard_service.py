"""Dashboard aggregation service."""
from datetime import datetime, timedelta, timezone

from repositories.aluno_repository import AlunoRepository
from repositories.avaliacao_repository import AvaliacaoRepository
from repositories.treino_repository import TreinoRepository
from repositories.protocolo_repository import ProtocoloRepository
from repositories.log_repository import LogRepository


class DashboardService:
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

    @staticmethod
    def feed(user_id: int) -> dict:
        return {
            "ultimos_alunos": AlunoRepository.recent_for_user(user_id, limit=5),
            "ultimas_avaliacoes": AvaliacaoRepository.latest_for_user(user_id, limit=5),
            "ultimos_treinos": TreinoRepository.recent_for_user(user_id, limit=5),
            "logs": LogRepository.latest_for_user(user_id, limit=8),
        }

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

    @staticmethod
    def atividade_semana(user_id: int) -> dict:
        hoje = datetime.now(timezone.utc).date()
        inicio = hoje - timedelta(days=6)
        avals_por_dia = AvaliacaoRepository.count_by_day(user_id, inicio, hoje)
        treinos_por_dia = TreinoRepository.count_created_by_day(user_id, inicio, hoje)
        labels = []
        avaliacoes_serie = []
        treinos_serie = []
        for i in range(7):
            dia = inicio + timedelta(days=i)
            labels.append(dia.strftime("%d/%m"))
            avaliacoes_serie.append(avals_por_dia.get(dia, 0))
            treinos_serie.append(treinos_por_dia.get(dia, 0))
        return {
            "labels": labels,
            "avaliacoes": avaliacoes_serie,
            "treinos": treinos_serie,
        }
