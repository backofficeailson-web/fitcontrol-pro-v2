"""Aluno business logic service."""
from datetime import datetime, UTC

from models.aluno import Aluno
from repositories.aluno_repository import AlunoRepository
from utils.security import sanitize_text


class AlunoService:
    @staticmethod
    def list_alunos(user_id: int, search: str | None = None, status: str | None = None) -> list[Aluno]:
        return AlunoRepository.list_for_user(user_id, search=search, status=status)

    @staticmethod
    def get_aluno(aluno_id: int, user_id: int) -> Aluno | None:
        return AlunoRepository.get_for_user(aluno_id, user_id)

    @staticmethod
    def create_aluno(user_id: int, data: dict) -> Aluno:
        aluno = Aluno(
            user_id=user_id,
            nome=sanitize_text(data.get("nome"), 160) or "",
            email=sanitize_text(data.get("email"), 180),
            telefone=sanitize_text(data.get("telefone"), 40),
            nascimento=data.get("nascimento"),
            sexo=sanitize_text(data.get("sexo"), 20),
            altura=data.get("altura"),
            peso_inicial=data.get("peso_inicial"),
            objetivo=sanitize_text(data.get("objetivo"), 120),
            observacoes=sanitize_text(data.get("observacoes"), 5000),
            status=data.get("status") or "ativo",
            condicoes_especiais=sanitize_text(data.get("condicoes_especiais"), 255),
            nivel_condicionamento=data.get("nivel_condicionamento") or "iniciante",
        )
        return AlunoRepository.add(aluno)

    @staticmethod
    def update_aluno(aluno: Aluno, data: dict) -> Aluno:
        aluno.nome = sanitize_text(data.get("nome"), 160) or aluno.nome
        aluno.email = sanitize_text(data.get("email"), 180)
        aluno.telefone = sanitize_text(data.get("telefone"), 40)
        aluno.nascimento = data.get("nascimento")
        aluno.sexo = sanitize_text(data.get("sexo"), 20)
        aluno.altura = data.get("altura")
        aluno.peso_inicial = data.get("peso_inicial")
        aluno.objetivo = sanitize_text(data.get("objetivo"), 120)
        aluno.observacoes = sanitize_text(data.get("observacoes"), 5000)
        aluno.status = data.get("status") or aluno.status
        aluno.condicoes_especiais = sanitize_text(data.get("condicoes_especiais"), 255)
        aluno.nivel_condicionamento = data.get("nivel_condicionamento") or aluno.nivel_condicionamento
        aluno.updated_at = datetime.now(UTC)
        AlunoRepository.save()
        return aluno

    @staticmethod
    def delete_aluno(aluno: Aluno) -> None:
        AlunoRepository.delete(aluno)
