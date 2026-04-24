from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ConfirmEmailRequest(BaseModel):
    """
    Тело запроса подтверждения email-адреса.

    Атрибуты:
        token: Токен верификации, полученный по email.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            },
        },
    )

    token: str = Field(
        ...,
        min_length=16,
        description="Токен верификации email (минимум 16 символов)",
    )
