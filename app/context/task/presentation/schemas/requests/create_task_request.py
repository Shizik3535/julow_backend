from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateTaskRequest(BaseModel):
    """Запрос на создание задачи."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Заголовок задачи",
        examples=["Implement login page"],
    )
    task_type: str = Field(
        default="TASK",
        description="Тип задачи (TASK, BUG, FEATURE, IMPROVEMENT, SUBTASK)",
        examples=["TASK"],
    )
    reporter_id: str | None = Field(
        default=None,
        description="UUID автора (None — текущий пользователь)",
        examples=["user-uuid"],
    )
    parent_task_id: str | None = Field(
        default=None,
        description="UUID родительской задачи (для подзадач)",
        examples=["parent-task-uuid"],
    )
    epic_id: str | None = Field(
        default=None,
        description="UUID эпика",
        examples=["epic-uuid"],
    )
