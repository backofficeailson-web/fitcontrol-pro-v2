"""Treino repository."""
from models import db
from models.treino import Treino
from repositories.base_repository import BaseRepository


class TreinoRepository(BaseRepository[Treino]):
    model = Treino

    @classmethod
    def list_for_user(cls, user_id: int, aluno_id: int | None = None, status: str | None = None) -> list[Treino]:
        query = db.session.query(Treino).filter(Treino.user_id == user_id)
        if aluno_id:
            query = query.filter(Treino.aluno_id == aluno_id)
        if status and status != "todos":
            query = query.filter(Treino.status == status)
        return query.order_by(Treino.created_at.desc()).all()

    @classmethod
    def get_for_user(cls, treino_id: int, user_id: int) -> Treino | None:
        return (
            db.session.query(Treino)
            .filter(Treino.id == treino_id, Treino.user_id == user_id)
            .first()
        )

    @classmethod
    def count_for_user(cls, user_id: int) -> int:
        return db.session.query(Treino).filter(Treino.user_id == user_id).count()

    @classmethod
    def count_active_for_user(cls, user_id: int) -> int:
        return (
            db.session.query(Treino)
            .filter(Treino.user_id == user_id, Treino.status == "ativo")
            .count()
        )

    @classmethod
    def recent_for_user(cls, user_id: int, limit: int = 5) -> list[Treino]:
        return (
            db.session.query(Treino)
            .filter(Treino.user_id == user_id)
            .order_by(Treino.created_at.desc())
            .limit(limit)
            .all()
        )
