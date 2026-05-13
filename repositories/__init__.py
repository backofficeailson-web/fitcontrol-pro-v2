"""Repositories package - data access layer abstractions."""
from repositories.user_repository import UserRepository
from repositories.aluno_repository import AlunoRepository
from repositories.avaliacao_repository import AvaliacaoRepository
from repositories.treino_repository import TreinoRepository
from repositories.exercicio_repository import ExercicioRepository
from repositories.protocolo_repository import ProtocoloRepository
from repositories.log_repository import LogRepository

__all__ = [
    "UserRepository",
    "AlunoRepository",
    "AvaliacaoRepository",
    "TreinoRepository",
    "ExercicioRepository",
    "ProtocoloRepository",
    "LogRepository",
]
