from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TeamResponse(BaseModel):
    """
    Ответ с данными команды.

    Атрибуты:
        id: UUID команды.
        org_id: UUID организации.
        name: Название команды.
        description: Описание.
        lead_id: UUID лидера команды.
        member_ids: Список UUID участников.
        icon: Название иконки.
        is_active: Активна ли команда.
        created_at: Дата создания (UTC).
        updated_at: Дата последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID команды",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    org_id: str = Field(
        ...,
        description="UUID организации",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    name: str = Field(
        ...,
        description="Название команды",
        examples=["Backend Team"],
    )
    description: str | None = Field(
        default=None,
        description="Описание команды",
        examples=["Команда разработки бэкенда"],
    )
    lead_id: str | None = Field(
        default=None,
        description="UUID лидера команды",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    member_ids: list[str] = Field(
        default_factory=list,
        description="Список UUID участников",
    )
    icon: str | None = Field(
        default=None,
        description="Название иконки",
        examples=["Code"],
    )
    is_active: bool = Field(default=True, description="Активна ли команда")
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
