from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MoveTaskRequest(BaseModel):
    """Запрос на перемещение задачи на доске (drag-n-drop)."""

    model_config = ConfigDict(from_attributes=True)

    column_id: str = Field(
        ...,
        description="UUID колонки доски",
        examples=["column-uuid"],
    )
    position: float = Field(
        ...,
        ge=0,
        description="Позиция в колонке",
        examples=[1.5],
    )
