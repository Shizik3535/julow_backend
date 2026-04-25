from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateSprintGoalRequest(BaseModel):
    """Запрос на обновление цели спринта."""

    model_config = ConfigDict(from_attributes=True)

    goal: str = Field(..., min_length=1, description="Новая цель спринта")
