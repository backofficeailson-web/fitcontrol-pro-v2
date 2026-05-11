"""Base repository - generic CRUD operations."""
from typing import Generic, Type, TypeVar

from sqlalchemy.exc import SQLAlchemyError

from models import db

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: Type[T]

    @classmethod
    def get(cls, entity_id: int) -> T | None:
        return db.session.get(cls.model, entity_id)

    @classmethod
    def all(cls) -> list[T]:
        return db.session.query(cls.model).all()

    @classmethod
    def add(cls, entity: T) -> T:
        try:
            db.session.add(entity)
            db.session.commit()
            return entity
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def save(cls) -> None:
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def delete(cls, entity: T) -> None:
        try:
            db.session.delete(entity)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise
