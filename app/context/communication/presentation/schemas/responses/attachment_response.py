from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttachmentResponse(BaseModel):
    """Ответ с данными вложения."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID вложения")
    file_id: str = Field(..., description="UUID файла из FileStorage BC")
    url: str | None = Field(default=None, description="URL файла")
    attachment_type: str = Field(default="file", description="Тип вложения")
    name: str = Field(default="", description="Имя файла")
    size_bytes: int = Field(default=0, description="Размер в байтах")
    preview_url: str | None = Field(default=None, description="URL превью")
    created_at: datetime | None = Field(default=None, description="Время создания (UTC)")
