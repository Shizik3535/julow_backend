from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RetroSectionSchema(BaseModel):
    """Секция retro-шаблона в запросе."""

    title: str = Field(..., min_length=1, max_length=100, description="Заголовок секции")
    prompt: str | None = Field(None, description="Подсказка для секции")
    item_type: str = Field(
        ..., description="Тип элементов: positive | negative | neutral | action_item", examples=["positive"]
    )


class UpdateRetroTemplateRequest(BaseModel):
    """Запрос на обновление шаблона ретроспективы."""

    model_config = ConfigDict(from_attributes=True)

    sections: list[RetroSectionSchema] | None = Field(None, description="Секции шаблона")
