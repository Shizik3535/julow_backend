from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RichTextSchema(BaseModel):
    """Форматированный текст."""

    content: str = Field(..., description="Содержимое")
    format: str = Field(..., description="Формат: markdown | wysiwyg", examples=["markdown"])


class CategorySchema(BaseModel):
    """Категория проекта."""

    name: str = Field(..., description="Название категории")
    color: str | None = Field(None, description="Цвет категории (HEX)")


class DateRangeSchema(BaseModel):
    """Диапазон дат."""

    start: date = Field(..., description="Дата начала")
    end: date = Field(..., description="Дата окончания")


class MilestoneResponse(BaseModel):
    """Данные milestone проекта."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID milestone")
    name: str = Field(..., description="Название milestone")
    description: RichTextSchema | None = Field(None, description="Описание")
    status: str = Field(..., description="Статус: not_started | in_progress | completed | overdue")
    due_date: str | None = Field(None, description="Дата дедлайна")
    completed_at: datetime | None = Field(None, description="Дата завершения (UTC)")


class CustomFieldDefinitionSchema(BaseModel):
    """Определение кастомного поля."""

    name: str = Field(..., description="Имя поля")
    field_type: str = Field(..., description="Тип: text | number | date | select | multi_select | url | user | checkbox")
    is_required: bool = Field(False, description="Обязательное ли поле")
    options: list[str] | None = Field(None, description="Опции для select/multi_select")
    default_value: str | None = Field(None, description="Значение по умолчанию")
    description: str | None = Field(None, description="Описание поля")


class ProjectResponse(BaseModel):
    """Ответ с данными проекта."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID проекта", examples=["550e8400-e29b-41d4-a716-446655440000"])
    workspace_id: str = Field(..., description="UUID workspace")
    name: str = Field(..., description="Название проекта", examples=["Backend API"])
    description: RichTextSchema | None = Field(None, description="Описание проекта")
    icon: str | None = Field(None, description="Иконка (emoji или URL)")
    color: str | None = Field(None, description="Акцентный цвет (HEX)", examples=["#3498DB"])
    category: CategorySchema | None = Field(None, description="Категория проекта")
    methodology: str = Field(..., description="Методология: kanban | scrum | waterfall | hybrid | shape_up", examples=["scrum"])
    visibility: str = Field(..., description="Видимость: private | workspace | organization | public", examples=["private"])
    status: str = Field(..., description="Статус: active | archived | suspended | pending_deletion", examples=["active"])
    owner_ids: list[str] = Field(default_factory=list, description="Список UUID владельцев")
    start_date: date | None = Field(None, description="Дата начала проекта")
    deadline: date | None = Field(None, description="Дедлайн проекта")
    milestones: list[MilestoneResponse] = Field(default_factory=list, description="Milestones проекта")
    custom_field_definitions: list[CustomFieldDefinitionSchema] = Field(
        default_factory=list, description="Кастомные поля проекта"
    )
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
