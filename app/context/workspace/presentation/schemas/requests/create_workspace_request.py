from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateWorkspaceRequest(BaseModel):
    """
    Запрос на создание workspace.

    Атрибуты:
        name: Название workspace (3–100 символов).
        workspace_type: Тип (PERSONAL, TEAM, ENTERPRISE). По умолчанию TEAM.
        organization_id: ID организации (None — автономный).
        parent_workspace_id: ID родительского workspace (None — корневой).
    """

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Название workspace",
        examples=["Development Team"],
    )
    workspace_type: str = Field(
        default="TEAM",
        description="Тип workspace (PERSONAL, TEAM, ENTERPRISE)",
        examples=["TEAM"],
    )
    organization_id: str | None = Field(
        default=None,
        description="UUID организации (None — автономный)",
        examples=["org-uuid"],
    )
    parent_workspace_id: str | None = Field(
        default=None,
        description="UUID родительского workspace (None — корневой)",
        examples=["parent-ws-uuid"],
    )
