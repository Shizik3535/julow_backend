from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.context.project.presentation.schemas.responses.project_response import RichTextSchema


class UpdateEpicRequest(BaseModel):
    """Запрос на обновление эпика."""

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(None, min_length=1, max_length=200, description="Название эпика")
    description: RichTextSchema | None = Field(None, description="Описание эпика")
    owner_id: str | None = Field(None, description="UUID владельца")
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Цвет эпика (HEX)")
    start_date: str | None = Field(None, description="Дата начала (ISO)")
    due_date: str | None = Field(None, description="Дата дедлайна (ISO)")
