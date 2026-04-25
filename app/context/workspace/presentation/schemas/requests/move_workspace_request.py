from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MoveWorkspaceRequest(BaseModel):
    """
    Запрос на перемещение workspace в иерархии.

    Атрибуты:
        parent_workspace_id: ID нового родителя (None — отсоединить от родителя).
    """

    model_config = ConfigDict(from_attributes=True)

    parent_workspace_id: str | None = Field(
        default=None,
        description="UUID нового родительского workspace (None — отсоединить)",
        examples=["parent-ws-uuid"],
    )
