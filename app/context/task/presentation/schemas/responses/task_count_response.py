from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TaskCountResponse(BaseModel):
    """Ответ со счётчиком задач."""

    model_config = ConfigDict(from_attributes=True)

    count: int = Field(..., description="Количество задач")
