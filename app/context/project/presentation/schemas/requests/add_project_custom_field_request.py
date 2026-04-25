from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AddProjectCustomFieldRequest(BaseModel):
    """Запрос на добавление кастомного поля проекта."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100, description="Название поля")
    field_type: str = Field(
        ..., description="Тип: text | number | date | select | multi_select | url | user | checkbox", examples=["text"]
    )
    is_required: bool = Field(False, description="Обязательное ли поле")
    options: list[str] | None = Field(None, description="Опции для select/multi_select")
    default_value: str | None = Field(None, description="Значение по умолчанию")
    description: str | None = Field(None, description="Описание поля")
