from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """
    Тело запроса входа в систему.

    Атрибуты:
        email: Email-адрес пользователя.
        password: Пароль.
        is_remember_me: Флаг «Запомнить меня» (увеличивает TTL сессии).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "StrongP@ss1",
                "is_remember_me": False,
            },
        },
    )

    email: EmailStr = Field(
        ...,
        description="Email-адрес пользователя",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Пароль пользователя",
    )
    is_remember_me: bool = Field(
        default=False,
        description="Запомнить меня — увеличивает время жизни сессии до 30 дней",
    )
