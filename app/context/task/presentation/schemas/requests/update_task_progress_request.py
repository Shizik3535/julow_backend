from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateTaskProgressRequest(BaseModel):
    """Запрос на обновление прогресса задачи."""

    model_config = ConfigDict(from_attributes=True)

    progress: int = Field(
        ...,
        ge=0,
        le=100,
        description="Прогресс задачи (0–100)",
        examples=[75],
    )
