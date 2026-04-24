from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PasswordResetConfirmRequest(BaseModel):
    """
    Тело запроса подтверждения сброса пароля.

    Выполняет смену пароля по ранее полученному токену.

    Атрибуты:
        email: Email-адрес пользователя.
        token: Токен сброса пароля.
        new_password: Новый пароль (минимум 8 символов).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                "new_password": "NewStr0ngP@ss!",
            },
        },
    )

    email: EmailStr = Field(
        ...,
        description="Email-адрес пользователя",
        examples=["user@example.com"],
    )
    token: str = Field(
        ...,
        min_length=16,
        description="Токен сброса пароля",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Новый пароль (от 8 до 128 символов)",
    )
