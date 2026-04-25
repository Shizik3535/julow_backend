from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectMemberResponse(BaseModel):
    """Ответ с данными участника проекта."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID записи участника")
    user_id: str = Field(..., description="UUID пользователя")
    role_id: str = Field(..., description="UUID роли проекта")
    joined_at: datetime | None = Field(None, description="Дата присоединения (UTC)")
    is_active: bool = Field(..., description="Активен ли участник")
