from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeTaskTypeRequest(BaseModel):
    """Запрос на смену типа задачи."""

    model_config = ConfigDict(from_attributes=True)

    task_type: str = Field(
        ...,
        description="Тип задачи (TASK, BUG, FEATURE, IMPROVEMENT, SUBTASK)",
        examples=["BUG"],
    )
