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


class CreateRetroTemplateRequest(BaseModel):
    """Запрос на создание шаблона ретроспективы."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=200, description="Название шаблона")
    sections: list[RetroSectionSchema] = Field(..., description="Секции шаблона")
