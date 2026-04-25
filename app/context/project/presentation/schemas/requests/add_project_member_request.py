from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddProjectMemberRequest(BaseModel):
    """Запрос на добавление участника в проект."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="UUID пользователя для добавления")
    role_id: str = Field(..., description="UUID роли проекта")
