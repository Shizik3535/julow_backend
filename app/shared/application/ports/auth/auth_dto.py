from __future__ import annotations

from uuid import UUID

from app.shared.application.base_dto import BaseDTO


class TokenPair(BaseDTO):
    """
    Пара JWT токенов (access + refresh).

    Атрибуты:
        access_token: Краткоживущий токен для авторизации запросов.
        refresh_token: Долгоживущий токен для обновления access_token.
        access_expires_in: Время жизни access_token в секундах.
        refresh_expires_in: Время жизни refresh_token в секундах.
    """

    access_token: str
    refresh_token: str
    access_expires_in: int
    refresh_expires_in: int


class AccessToken(BaseDTO):
    """
    JWT access токен.

    Атрибуты:
        access_token: Краткоживущий токен для авторизации запросов.
        access_expires_in: Время жизни access_token в секундах.
    """

    access_token: str
    access_expires_in: int


class TokenPayload(BaseDTO):
    """
    Расшифрованные данные JWT токена.

    Атрибуты:
        user_id: Идентификатор пользователя.
        token_type: Тип токена ("access" или "refresh").
        exp: Время истечения (Unix timestamp).
    """

    user_id: UUID
    token_type: str
    exp: int
