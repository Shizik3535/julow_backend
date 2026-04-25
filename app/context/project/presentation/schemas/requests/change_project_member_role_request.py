from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeProjectMemberRoleRequest(BaseModel):
    """Запрос на смену роли участника проекта."""

    model_config = ConfigDict(from_attributes=True)

    new_role_id: str = Field(..., description="UUID новой роли проекта")
