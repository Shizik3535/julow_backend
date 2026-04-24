from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RefreshSessionRequest(BaseModel):
    """
    Тело запроса обновления сессии по refresh-токену.

    Атрибуты:
        refresh_token: Текущий refresh-токен для обновления пары токенов.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            },
        },
    )

    refresh_token: str = Field(
        ...,
        min_length=1,
        description="JWT refresh-токен для обновления access-токена",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
