from __future__ import annotations

from app.shared.application.base_dto import BaseDTO
from app.context.identity.application.dto.user_dto import UserDTO


class AuthResultDTO(BaseDTO):
    """
    DTO результата аутентификации (Identity BC).

    Возвращается при успешном логине.

    Атрибуты:
        user: Данные пользователя.
        access_token: JWT access токен.
        refresh_token: JWT refresh токен.
        access_expires_in: Время жизни access токена в секундах.
        refresh_expires_in: Время жизни refresh токена в секундах.
    """

    user: UserDTO
    access_token: str
    refresh_token: str
    access_expires_in: int
    refresh_expires_in: int
