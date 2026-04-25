from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RetroSectionResponse(BaseModel):
    """Данные секции retro-шаблона."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., description="Заголовок секции")
    prompt: str | None = Field(None, description="Подсказка для секции")
    item_type: str = Field(..., description="Тип элементов: positive | negative | neutral | action_item")


class RetroTemplateResponse(BaseModel):
    """Ответ с данными retro-шаблона."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="UUID шаблона")
    name: str = Field(..., description="Название шаблона", examples=["classic"])
    sections: list[RetroSectionResponse] = Field(default_factory=list, description="Секции шаблона")
    is_system: bool = Field(..., description="Является ли системным шаблоном")
    created_at: datetime | None = Field(None, description="Дата создания (UTC)")
    updated_at: datetime | None = Field(None, description="Дата последнего обновления (UTC)")
