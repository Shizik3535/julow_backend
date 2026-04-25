from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddTaskRelationRequest(BaseModel):
    """Запрос на добавление связи между задачами."""

    model_config = ConfigDict(from_attributes=True)

    related_task_id: str = Field(
        ...,
        description="UUID связанной задачи",
        examples=["related-task-uuid"],
    )
    relation_type: str = Field(
        ...,
        description="Тип связи (BLOCKS, IS_BLOCKED_BY, RELATES_TO, DUPLICATES, IS_DUPLICATED_BY, CLONES, IS_CLONED_BY)",
        examples=["BLOCKS"],
    )
