from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BulkUpdateTasksRequest(BaseModel):
    """Запрос на массовое обновление задач."""

    model_config = ConfigDict(from_attributes=True)

    task_ids: list[str] = Field(
        ...,
        min_length=1,
        description="Список UUID задач",
        examples=[["task-uuid-1", "task-uuid-2"]],
    )
    changes: dict[str, str] = Field(
        ...,
        description="Словарь изменений (field → value). Допустимые ключи: status_id, priority, sprint_id, epic_id",
        examples=[{"priority": "HIGH", "sprint_id": "sprint-uuid"}],
    )
