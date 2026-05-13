"""Authentication service."""
import logging
from datetime import datetime, UTC, timedelta

from models.user import User
from repositories.user_repository import UserRepository
from repositories.log_repository import LogRepository

LOCK_THRESHOLD = 5
LOCK_DURATION_MINUTES = 15
auth_logger = logging.getLogger("fitcontrol.auth")


class AuthService:
    @staticmethod
    def register(*, nome: str, email: str, password: str, cref: str | None = None) -> User:
        if UserRepository.email_exists(email):
            raise ValueError("Já existe uma conta cadastrada com este e-mail.")
        user = UserRepository.create(nome=nome, email=email, password=password, cref=cref)
        auth_logger.info("New user registered: %s", user.email)
        LogRepository.write(
            category="auth", level="INFO",
            message=f"Cadastro realizado: {user.email}",
            user_id=user.id,
        )
        return user

    @staticmethod
    def authenticate(email: str, password: str, ip_address: str | None = None) -> User:
        user = UserRepository.get_by_email(email)
        if not user:
            auth_logger.warning("Login failed - email not found: %s", email)
            raise ValueError("Credenciais inválidas.")
        if user.is_locked():
            auth_logger.warning("Login attempt on locked account: %s", email)
            raise ValueError("Conta temporariamente bloqueada. Tente novamente em instantes.")
        if not user.check_password(password):
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= LOCK_THRESHOLD:
                user.locked_until = datetime.now(UTC) + timedelta(minutes=LOCK_DURATION_MINUTES)
                auth_logger.warning("Account locked: %s", email)
            UserRepository.save()
            LogRepository.write(
                category="auth", level="WARNING",
                message=f"Tentativa inválida de login: {email}",
                user_id=user.id, ip_address=ip_address,
            )
            raise ValueError("Credenciais inválidas.")
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(UTC)
        UserRepository.save()
        auth_logger.info("Login successful: %s", email)
        LogRepository.write(
            category="auth", level="INFO",
            message=f"Login realizado: {email}",
            user_id=user.id, ip_address=ip_address,
        )
        return user

    @staticmethod
    def update_password(user: User, current_password: str, new_password: str) -> None:
        if not user.check_password(current_password):
            raise ValueError("Senha atual incorreta.")
        if len(new_password) < 8:
            raise ValueError("A nova senha deve ter no mínimo 8 caracteres.")
        user.set_password(new_password)
        UserRepository.save()
        LogRepository.write(
            category="auth", level="INFO",
            message=f"Senha atualizada: {user.email}",
            user_id=user.id,
        )
