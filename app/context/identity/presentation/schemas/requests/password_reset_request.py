from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RequestPasswordResetRequest(BaseModel):
    """
    Тело запроса на сброс пароля.

    Отправляет токен сброса на указанный email.
    Если пользователь не найден — ответ всё равно 200
    (для предотвращения утечки информации о существовании аккаунта).

    Атрибуты:
        email: Email-адрес пользователя.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
            },
        },
    )

    email: EmailStr = Field(
        ...,
        description="Email-адрес пользователя для сброса пароля",
        examples=["user@example.com"],
    )
