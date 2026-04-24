from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangePasswordRequest(BaseModel):
    """
    Тело запроса смены пароля.

    Атрибуты:
        current_password: Текущий пароль пользователя.
        new_password: Новый пароль (минимум 8 символов).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "OldP@ssw0rd",
                "new_password": "NewStr0ngP@ss!",
            },
        },
    )

    current_password: str = Field(
        ...,
        min_length=1,
        description="Текущий пароль пользователя",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Новый пароль (от 8 до 128 символов)",
    )
