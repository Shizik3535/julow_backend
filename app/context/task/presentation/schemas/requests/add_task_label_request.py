from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddTaskLabelRequest(BaseModel):
    """Запрос на добавление метки задаче."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название метки",
        examples=["bug"],
    )
    color: str | None = Field(
        default=None,
        description="Цвет метки (HEX, например #FF0000)",
        examples=["#FF0000"],
    )
