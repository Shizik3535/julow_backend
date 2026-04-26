from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.context.project.presentation.schemas.responses.project_response import (
    CategorySchema,
    RichTextSchema,
)


class CreateProjectRequest(BaseModel):
    """Запрос на создание проекта."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=3, max_length=200, description="Название проекта", examples=["Backend API"])
    methodology: Literal["kanban", "scrum", "waterfall", "hybrid", "shape_up"] = Field(
        ..., description="Методология: kanban | scrum | waterfall | hybrid | shape_up", examples=["scrum"]
    )
    owner_id: str | None = Field(None, description="UUID владельца (по умолчанию — текущий пользователь)")
    description: RichTextSchema | None = Field(None, description="Описание проекта")
    visibility: str | None = Field(
        None, description="Видимость: private | workspace | organization | public", examples=["private"]
    )
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Акцентный цвет (HEX)", examples=["#3498DB"])
    icon: str | None = Field(None, description="Иконка (emoji или URL)")
    category: CategorySchema | None = Field(None, description="Категория проекта")
    start_date: date | None = Field(None, description="Дата начала проекта")
    deadline: date | None = Field(None, description="Дедлайн проекта")
