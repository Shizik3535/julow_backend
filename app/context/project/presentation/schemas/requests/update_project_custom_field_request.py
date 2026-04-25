from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateProjectCustomFieldRequest(BaseModel):
    """Запрос на обновление кастомного поля проекта."""

    model_config = ConfigDict(from_attributes=True)

    new_name: str | None = Field(None, min_length=1, max_length=100, description="Новое название поля")
    field_type: str | None = Field(None, description="Тип: text | number | date | select | multi_select | url | user | checkbox")
    is_required: bool = Field(False, description="Обязательное ли поле")
    options: list[str] | None = Field(None, description="Опции для select/multi_select")
    default_value: str | None = Field(None, description="Значение по умолчанию")
    description: str | None = Field(None, description="Описание поля")
