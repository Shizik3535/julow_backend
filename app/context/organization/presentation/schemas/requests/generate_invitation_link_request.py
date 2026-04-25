from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GenerateInvitationLinkRequest(BaseModel):
    """
    Тело запроса генерации ссылки-приглашения.

    Атрибуты:
        role_id: UUID роли.
        max_uses: Максимум использований (None — без ограничений).
        expires_in_hours: Время жизни ссылки в часах (None — без ограничений).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role_id": "770e8400-e29b-41d4-a716-446655440002",
                "max_uses": 10,
                "expires_in_hours": 72,
            },
        },
    )

    role_id: str = Field(
        ...,
        description="UUID роли",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    max_uses: int | None = Field(
        default=None,
        ge=1,
        description="Максимум использований (None — без ограничений)",
        examples=[10],
    )
    expires_in_hours: int | None = Field(
        default=None,
        ge=1,
        description="Время жизни ссылки в часах (None — без ограничений)",
        examples=[72],
    )
