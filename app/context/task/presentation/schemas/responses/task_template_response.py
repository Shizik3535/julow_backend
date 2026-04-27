from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TaskTemplateChecklistResponse(BaseModel):
    """Чек-лист шаблона задачи (упрощённый)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str


class TaskTemplateResponse(BaseModel):
    """Ответ с данными шаблона задачи."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str = Field(..., description="Название шаблона")
    description: dict[str, Any] | None = Field(default=None, description="Описание (content + format)")
    task_type: str = Field(..., description="Тип задачи")
    default_labels: list[dict[str, Any]] = Field(default_factory=list, description="Метки по умолчанию")
    default_checklists: list[dict[str, Any]] = Field(default_factory=list, description="Чек-листы по умолчанию")
    default_custom_fields: dict[str, str] = Field(default_factory=dict, description="Кастомные поля по умолчанию")
    is_system: bool = Field(..., description="Системный шаблон")
    created_at: datetime | str | None = Field(default=None, description="Время создания")
    updated_at: datetime | str | None = Field(default=None, description="Время обновления")
