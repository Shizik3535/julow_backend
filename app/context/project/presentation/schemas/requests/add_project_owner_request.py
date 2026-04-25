from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddProjectOwnerRequest(BaseModel):
    """Запрос на добавление со-владельца проекта."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str = Field(..., description="UUID нового со-владельца")
