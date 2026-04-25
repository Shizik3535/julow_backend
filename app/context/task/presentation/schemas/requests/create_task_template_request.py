from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateTaskTemplateRequest(BaseModel):
    """Запрос на создание шаблона задачи."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Название шаблона",
        examples=["Bug Report"],
    )
    task_type: str = Field(
        default="TASK",
        description="Тип задачи (TASK, BUG, FEATURE, IMPROVEMENT, SUBTASK)",
        examples=["BUG"],
    )
