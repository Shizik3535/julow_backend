from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreateProjectViewRequest(BaseModel):
    """Запрос на создание представления проекта."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., min_length=1, max_length=100, description="Название представления")
    view_type: str = Field(
        ..., description="Тип: board | list | timeline | calendar | table", examples=["board"]
    )
    config: dict[str, Any] | None = Field(None, description="Конфигурация представления")
    is_default: bool = Field(False, description="Является ли представлением по умолчанию")
    is_shared: bool = Field(False, description="Является ли общим представлением")
