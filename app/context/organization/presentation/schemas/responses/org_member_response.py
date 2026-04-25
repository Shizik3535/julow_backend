from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrgMemberResponse(BaseModel):
    """
    Ответ с данными участника организации.

    Атрибуты:
        id: UUID записи участника.
        user_id: UUID пользователя из Identity BC.
        display_name: Отображаемое имя в рамках организации.
        role_id: UUID роли.
        joined_at: Время присоединения.
        is_active: Активен ли участник.
        invited_by: UUID пригласившего.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID записи участника",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    user_id: str = Field(
        ...,
        description="UUID пользователя",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    display_name: str | None = Field(
        default=None,
        description="Отображаемое имя",
        examples=["Иван Петров"],
    )
    role_id: str = Field(
        default="",
        description="UUID роли",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    joined_at: datetime = Field(..., description="Время присоединения (UTC)")
    is_active: bool = Field(default=True, description="Активен ли участник")
    invited_by: str | None = Field(
        default=None,
        description="UUID пригласившего",
        examples=["880e8400-e29b-41d4-a716-446655440003"],
    )
