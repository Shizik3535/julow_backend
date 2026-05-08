from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.logging import get_logger
from app.shared.application.ports.auth.password_port import PasswordPort

logger = get_logger(__name__)


class Argon2PasswordAdapter(PasswordPort):
    """
    Реализация PasswordPort на основе argon2-cffi.

    Использует Argon2id через argon2-cffi — рекомендованную библиотеку
    для хеширования паролей в Python. Автоматически генерирует соль
    и обеспечивает constant-time верификацию.
    """

    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        hashed = self._hasher.hash(password)
        logger.debug("Password hashed")
        return hashed

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            result = self._hasher.verify(password_hash, password)
        except VerifyMismatchError:
            logger.debug("Password verification failed: mismatch")
            return False
        except InvalidHashError:
            logger.warning(
                "Password verification failed: unrecognized hash format",
            )
            return False
        logger.debug("Password verification succeeded")
        return result
