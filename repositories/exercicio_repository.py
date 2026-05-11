"""Exercicio repository."""
from models import db
from models.exercicio import Exercicio
from models.treino import Treino
from repositories.base_repository import BaseRepository


class ExercicioRepository(BaseRepository[Exercicio]):
    model = Exercicio

    @classmethod
    def list_for_treino(cls, treino_id: int, user_id: int) -> list[Exercicio]:
        return (
            db.session.query(Exercicio)
            .join(Treino, Treino.id == Exercicio.treino_id)
            .filter(Treino.id == treino_id, Treino.user_id == user_id)
            .order_by(Exercicio.dia_semana.asc(), Exercicio.ordem.asc())
            .all()
        )

    @classmethod
    def get_for_user(cls, exercicio_id: int, user_id: int) -> Exercicio | None:
        return (
            db.session.query(Exercicio)
            .join(Treino, Treino.id == Exercicio.treino_id)
            .filter(Exercicio.id == exercicio_id, Treino.user_id == user_id)
            .first()
        )

    @classmethod
    def delete_all_for_treino(cls, treino_id: int) -> None:
        db.session.query(Exercicio).filter(Exercicio.treino_id == treino_id).delete()
        db.session.commit()
