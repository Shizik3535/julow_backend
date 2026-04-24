from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.context.identity.presentation.schemas.responses.user_response import UserResponse


class LoginResponse(BaseModel):
    """
    Ответ при успешной аутентификации.

    Возвращает данные пользователя и пару JWT-токенов
    (access + refresh) с информацией о времени жизни.

    Атрибуты:
        user: Данные пользователя.
        access_token: JWT access-токен для авторизации запросов.
        refresh_token: JWT refresh-токен для обновления access-токена.
        access_expires_in: Время жизни access-токена в секундах.
        refresh_expires_in: Время жизни refresh-токена в секундах.
    """

    model_config = ConfigDict(from_attributes=True)

    user: UserResponse = Field(..., description="Данные пользователя")
    access_token: str = Field(..., description="JWT access-токен")
    refresh_token: str = Field(..., description="JWT refresh-токен")
    access_expires_in: int = Field(..., description="TTL access-токена (секунды)", examples=[1800])
    refresh_expires_in: int = Field(..., description="TTL refresh-токена (секунды)", examples=[604800])
