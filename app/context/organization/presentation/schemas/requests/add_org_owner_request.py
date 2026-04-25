from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddOrgOwnerRequest(BaseModel):
    """
    Тело запроса добавления владельца организации.

    Атрибуты:
        user_id: UUID пользователя, которого нужно назначить владельцем.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        },
    )

    user_id: str = Field(
        ...,
        description="UUID пользователя",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
