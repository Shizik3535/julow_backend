from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChangeTaskPriorityRequest(BaseModel):
    """Запрос на смену приоритета задачи."""

    model_config = ConfigDict(from_attributes=True)

    priority: str = Field(
        ...,
        description="Приоритет (LOW, MEDIUM, HIGH, CRITICAL, URGENT)",
        examples=["HIGH"],
    )
