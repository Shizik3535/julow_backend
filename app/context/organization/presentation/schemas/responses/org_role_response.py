from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrgRoleResponse(BaseModel):
    """
    Ответ с данными роли организации.

    Атрибуты:
        id: UUID роли.
        org_id: UUID организации.
        name: Название роли.
        permissions: Список разрешений.
        is_system: Является ли роль системной.
        description: Описание роли.
        scope: Область действия роли.
        created_at: Дата создания (UTC).
        updated_at: Дата последнего обновления (UTC).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID роли",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    org_id: str = Field(
        default="",
        description="UUID организации (пусто для системных ролей)",
        examples=["660e8400-e29b-41d4-a716-446655440001"],
    )
    name: str = Field(
        default="",
        description="Название роли",
        examples=["member"],
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Список разрешений",
        examples=[["members.read", "tasks.write"]],
    )
    is_system: bool = Field(
        default=False,
        description="Является ли роль системной",
    )
    description: str | None = Field(
        default=None,
        description="Описание роли",
        examples=["Роль участника по умолчанию"],
    )
    scope: str = Field(
        default="ORG",
        description="Область действия роли",
        examples=["ORG"],
    )
    created_at: datetime = Field(..., description="Дата создания (UTC)")
    updated_at: datetime = Field(..., description="Дата последнего обновления (UTC)")
