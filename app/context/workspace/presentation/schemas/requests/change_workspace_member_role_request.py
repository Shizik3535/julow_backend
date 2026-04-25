from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeWorkspaceMemberRoleRequest(BaseModel):
    """
    Запрос на смену роли участника workspace.

    Атрибуты:
        new_role_id: ID новой роли.
    """

    model_config = ConfigDict(from_attributes=True)

    new_role_id: str = Field(..., description="UUID новой роли", examples=["role-uuid"])
