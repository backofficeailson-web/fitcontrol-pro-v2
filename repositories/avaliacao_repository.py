"""Avaliacao repository."""
from models import db
from models.avaliacao import Avaliacao
from repositories.base_repository import BaseRepository


class AvaliacaoRepository(BaseRepository[Avaliacao]):
    model = Avaliacao

    @classmethod
    def list_for_user(cls, user_id: int, aluno_id: int | None = None) -> list[Avaliacao]:
        query = db.session.query(Avaliacao).filter(Avaliacao.user_id == user_id)
        if aluno_id:
            query = query.filter(Avaliacao.aluno_id == aluno_id)
        return query.order_by(Avaliacao.data.desc(), Avaliacao.id.desc()).all()

    @classmethod
    def get_for_user(cls, avaliacao_id: int, user_id: int) -> Avaliacao | None:
        return (
            db.session.query(Avaliacao)
            .filter(Avaliacao.id == avaliacao_id, Avaliacao.user_id == user_id)
            .first()
        )

    @classmethod
    def count_for_user(cls, user_id: int) -> int:
        return db.session.query(Avaliacao).filter(Avaliacao.user_id == user_id).count()

    @classmethod
    def latest_for_user(cls, user_id: int, limit: int = 5) -> list[Avaliacao]:
        return (
            db.session.query(Avaliacao)
            .filter(Avaliacao.user_id == user_id)
            .order_by(Avaliacao.created_at.desc())
            .limit(limit)
            .all()
        )

    @classmethod
    def history_for_aluno(cls, aluno_id: int, user_id: int) -> list[Avaliacao]:
        return (
            db.session.query(Avaliacao)
            .filter(Avaliacao.aluno_id == aluno_id, Avaliacao.user_id == user_id)
            .order_by(Avaliacao.data.asc())
            .all()
        )
