from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceResponse(BaseModel):
    """
    Ответ с данными workspace.

    Атрибуты:
        id: UUID workspace.
        name: Название workspace.
        status: Статус (ACTIVE, ARCHIVED, SUSPENDED, PENDING_DELETION).
        workspace_type: Тип (PERSONAL, TEAM, ENTERPRISE).
        organization_id: ID организации (None — автономный).
        parent_workspace_id: ID родительского workspace (None — корневой).
        personalization: Настройки персонализации (dict).
        owner_ids: Список ID владельцев.
        security_policy: Политика безопасности (dict).
        membership_policy: Политика членства (dict).
        limits: Лимиты workspace (dict).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID workspace",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    name: str = Field(..., description="Название workspace", examples=["Development Team"])
    status: str = Field(..., description="Статус workspace", examples=["ACTIVE"])
    workspace_type: str = Field(..., description="Тип workspace", examples=["TEAM"])
    organization_id: str | None = Field(
        default=None,
        description="ID организации (None — автономный)",
        examples=["org-uuid"],
    )
    parent_workspace_id: str | None = Field(
        default=None,
        description="ID родительского workspace (None — корневой)",
        examples=["parent-ws-uuid"],
    )
    personalization: dict[str, Any] | None = Field(
        default=None,
        description="Настройки персонализации",
    )
    owner_ids: list[str] | None = Field(
        default=None,
        description="Список ID владельцев",
    )
    security_policy: dict[str, Any] | None = Field(
        default=None,
        description="Политика безопасности",
    )
    membership_policy: dict[str, Any] | None = Field(
        default=None,
        description="Политика членства",
    )
    limits: dict[str, Any] | None = Field(
        default=None,
        description="Лимиты workspace",
    )
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
