"""User repository."""
from models import db
from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    @classmethod
    def get_by_email(cls, email: str) -> User | None:
        if not email:
            return None
        return db.session.query(User).filter(User.email == email.lower().strip()).first()

    @classmethod
    def email_exists(cls, email: str) -> bool:
        return cls.get_by_email(email) is not None

    @classmethod
    def create(cls, *, nome: str, email: str, password: str, cref: str | None = None) -> User:
        user = User(nome=nome.strip(), email=email.lower().strip(), cref=cref)
        user.set_password(password)
        return cls.add(user)
