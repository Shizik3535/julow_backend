from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChangeWorkspaceMemberRoleRequest(BaseModel):
    """
    Запрос на смену роли участника workspace.

    Атрибуты:
        new_role_id: ID новой роли.
    """

    model_config = ConfigDict(from_attributes=True)

    new_role_id: UUID = Field(..., description="UUID новой роли", examples=["role-uuid"])
