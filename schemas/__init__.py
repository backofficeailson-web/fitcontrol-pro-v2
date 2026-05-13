"""Schemas (Flask-WTF forms) package."""
from schemas.auth_forms import LoginForm, RegisterForm, ChangePasswordForm
from schemas.aluno_forms import AlunoForm
from schemas.avaliacao_forms import AvaliacaoForm
from schemas.treino_forms import TreinoForm, ExercicioForm, GerarTreinoIAForm

__all__ = [
    "LoginForm",
    "RegisterForm",
    "ChangePasswordForm",
    "AlunoForm",
    "AvaliacaoForm",
    "TreinoForm",
    "ExercicioForm",
    "GerarTreinoIAForm",
]
