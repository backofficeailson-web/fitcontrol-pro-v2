"""Models package - SQLAlchemy database instance and model registry."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User  # noqa: E402,F401
from models.aluno import Aluno  # noqa: E402,F401
from models.avaliacao import Avaliacao  # noqa: E402,F401
from models.treino import Treino  # noqa: E402,F401
from models.exercicio import Exercicio  # noqa: E402,F401
from models.protocolo import Protocolo  # noqa: E402,F401
from models.log_entry import LogEntry  # noqa: E402,F401
from models.postura import AvaliacaoPostural  # noqa: E402,F401
from models.ai_analysis import AIAnalysis  # noqa: E402,F401

__all__ = [
    "db",
    "User",
    "Aluno",
    "Avaliacao",
    "Treino",
    "Exercicio",
    "Protocolo",
    "LogEntry",
    "AvaliacaoPostural",
    "AIAnalysis",
]
