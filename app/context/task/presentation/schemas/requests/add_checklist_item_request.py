from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddChecklistItemRequest(BaseModel):
    """Запрос на добавление пункта чек-листа."""

    model_config = ConfigDict(from_attributes=True)

    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Текст пункта",
        examples=["Deploy to staging"],
    )
    assignee_id: str | None = Field(
        default=None,
        description="UUID исполнителя пункта",
        examples=["user-uuid"],
    )
    due_date: str | None = Field(
        default=None,
        description="Срок выполнения (ISO)",
        examples=["2025-01-20"],
    )
