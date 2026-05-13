"""Aluno repository - user-scoped queries."""
from sqlalchemy import or_

from models import db
from models.aluno import Aluno
from repositories.base_repository import BaseRepository


class AlunoRepository(BaseRepository[Aluno]):
    model = Aluno

    @classmethod
    def list_for_user(cls, user_id: int, search: str | None = None, status: str | None = None) -> list[Aluno]:
        query = db.session.query(Aluno).filter(Aluno.user_id == user_id)
        if search:
            term = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    db.func.lower(Aluno.nome).like(term),
                    db.func.lower(Aluno.email).like(term),
                )
            )
        if status and status != "todos":
            query = query.filter(Aluno.status == status)
        return query.order_by(Aluno.nome.asc()).all()

    @classmethod
    def get_for_user(cls, aluno_id: int, user_id: int) -> Aluno | None:
        return (
            db.session.query(Aluno)
            .filter(Aluno.id == aluno_id, Aluno.user_id == user_id)
            .first()
        )

    @classmethod
    def count_for_user(cls, user_id: int) -> int:
        return db.session.query(Aluno).filter(Aluno.user_id == user_id).count()

    @classmethod
    def count_active_for_user(cls, user_id: int) -> int:
        return (
            db.session.query(Aluno)
            .filter(Aluno.user_id == user_id, Aluno.status == "ativo")
            .count()
        )

    @classmethod
    def recent_for_user(cls, user_id: int, limit: int = 5) -> list[Aluno]:
        return (
            db.session.query(Aluno)
            .filter(Aluno.user_id == user_id)
            .order_by(Aluno.created_at.desc())
            .limit(limit)
            .all()
        )
