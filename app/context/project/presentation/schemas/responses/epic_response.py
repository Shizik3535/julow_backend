from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.context.project.presentation.schemas.responses.project_response import RichTextSchema


class EpicResponse(BaseModel):
    """Ответ с данными эпика."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID эпика")
    project_id: str = Field(..., description="UUID проекта")
    name: str = Field(..., description="Название эпика")
    description: RichTextSchema | None = Field(None, description="Описание эпика")
    status: str = Field(..., description="Статус: open | in_progress | done | cancelled")
    start_date: str | None = Field(None, description="Дата начала")
    due_date: str | None = Field(None, description="Дата дедлайна")
    owner_id: str | None = Field(None, description="UUID владельца")
    color: str | None = Field(None, description="Цвет эпика (HEX)")
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
