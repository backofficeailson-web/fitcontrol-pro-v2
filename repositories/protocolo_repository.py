"""Protocolo repository."""
from models import db
from models.protocolo import Protocolo
from repositories.base_repository import BaseRepository


class ProtocoloRepository(BaseRepository[Protocolo]):
    model = Protocolo

    @classmethod
    def list_for_user(cls, user_id: int, aluno_id: int | None = None) -> list[Protocolo]:
        query = db.session.query(Protocolo).filter(Protocolo.user_id == user_id)
        if aluno_id:
            query = query.filter(Protocolo.aluno_id == aluno_id)
        return query.order_by(Protocolo.created_at.desc()).all()

    @classmethod
    def count_active_for_user(cls, user_id: int) -> int:
        return (
            db.session.query(Protocolo)
            .filter(Protocolo.user_id == user_id, Protocolo.status == "ativo")
            .count()
        )

    @classmethod
    def get_for_user(cls, protocolo_id: int, user_id: int) -> Protocolo | None:
        return (
            db.session.query(Protocolo)
            .filter(Protocolo.id == protocolo_id, Protocolo.user_id == user_id)
            .first()
        )
