from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.context.project.presentation.schemas.responses.project_response import (
    CategorySchema,
    RichTextSchema,
)


class UpdateProjectInfoRequest(BaseModel):
    """Запрос на обновление информации проекта."""

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(None, min_length=3, max_length=200, description="Название проекта")
    description: RichTextSchema | None = Field(None, description="Описание проекта")
    icon: str | None = Field(None, description="Иконка (emoji или URL)")
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Акцентный цвет (HEX)")
    category: CategorySchema | None = Field(None, description="Категория проекта")
    start_date: date | None = Field(None, description="Дата начала проекта")
    deadline: date | None = Field(None, description="Дедлайн проекта")
