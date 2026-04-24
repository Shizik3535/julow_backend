from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """
    Тело запроса регистрации нового пользователя.

    Атрибуты:
        email: Валидный email-адрес.
        password: Пароль (минимум 8 символов).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "StrongP@ss1",
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
        min_length=8,
        max_length=128,
        description="Пароль (от 8 до 128 символов)",
    )
