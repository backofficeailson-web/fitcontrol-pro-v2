"""Services package - business logic layer."""
from services.auth_service import AuthService
from services.aluno_service import AlunoService
from services.avaliacao_service import AvaliacaoService
from services.treino_service import TreinoService
from services.protocolo_service import ProtocoloService
from services.dashboard_service import DashboardService
from services.pdf_service import PDFService
from services.ai_engine import AIEngine

__all__ = [
    "AuthService",
    "AlunoService",
    "AvaliacaoService",
    "TreinoService",
    "ProtocoloService",
    "DashboardService",
    "PDFService",
    "AIEngine",
]
