from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddWorkflowStatusRequest(BaseModel):
    """Запрос на добавление статуса workflow."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100, description="Название статуса")
    category: str = Field(
        "todo", description="Категория: todo | in_progress | done | cancelled | blocked | review", examples=["todo"]
    )
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Цвет статуса (HEX)")
    icon: str | None = Field(None, description="Иконка статуса")
    is_default: bool = Field(False, description="Является ли начальным статусом")
