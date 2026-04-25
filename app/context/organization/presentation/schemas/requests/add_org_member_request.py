from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddOrgMemberRequest(BaseModel):
    """
    Тело запроса добавления участника в организацию.

    Атрибуты:
        user_id: UUID пользователя.
        role_id: UUID роли (None — используется default_role).
        display_name: Отображаемое имя.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "role_id": "660e8400-e29b-41d4-a716-446655440001",
                "display_name": "Иван Петров",
            },
        },
    )

    user_id: str = Field(
        ...,
        description="UUID пользователя",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    role_id: str | None = Field(
        default=None,
        description="UUID роли (None — default_role из MembershipPolicy)",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    display_name: str | None = Field(
        default=None,
        max_length=255,
        description="Отображаемое имя",
        examples=["Иван Петров"],
    )
