from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SetTaskCustomFieldRequest(BaseModel):
    """Запрос на установку кастомного поля задачи."""

    model_config = ConfigDict(from_attributes=True)

    field_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Имя кастомного поля",
        examples=["environment"],
    )
    value: str = Field(
        ...,
        description="Значение кастомного поля",
        examples=["production"],
    )
