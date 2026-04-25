from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UpdateTaskTemplateRequest(BaseModel):
    """Запрос на обновление шаблона задачи."""

    model_config = ConfigDict(from_attributes=True)

    default_labels: list[dict[str, Any]] | None = Field(
        default=None,
        description="Метки по умолчанию [{'name': '...', 'color': '#...'}]",
        examples=[[{"name": "bug", "color": "#FF0000"}]],
    )
    default_checklists: list[dict[str, Any]] | None = Field(
        default=None,
        description="Чек-листы по умолчанию [{'title': '...'}]",
        examples=[[{"title": "Steps to reproduce"}]],
    )
    default_custom_fields: dict[str, str] | None = Field(
        default=None,
        description="Кастомные поля по умолчанию",
        examples=[{"environment": "production"}],
    )
