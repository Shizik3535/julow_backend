from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceTeamResponse(BaseModel):
    """
    Ответ с данными команды workspace.

    Атрибуты:
        id: Идентификатор команды.
        workspace_id: ID workspace.
        name: Название команды.
        description: Описание.
        lead_id: ID лидера.
        member_ids: Список ID участников.
        icon_url: URL иконки.
        is_active: Активна ли команда.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID команды",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    workspace_id: str = Field(
        ...,
        description="UUID workspace",
        examples=["ws-uuid"],
    )
    name: str = Field(..., description="Название команды", examples=["Backend Team"])
    description: str | None = Field(
        default=None,
        description="Описание команды",
        examples=["Backend development team"],
    )
    lead_id: str | None = Field(
        default=None,
        description="UUID лидера команды",
        examples=["lead-uuid"],
    )
    member_ids: list[str] | None = Field(
        default=None,
        description="Список UUID участников команды",
    )
    icon_url: str | None = Field(
        default=None,
        description="URL иконки команды",
        examples=["https://example.com/icon.png"],
    )
    is_active: bool = Field(default=True, description="Активна ли команда")
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
