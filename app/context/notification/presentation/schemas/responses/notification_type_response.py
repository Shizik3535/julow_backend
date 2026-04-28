from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class NotificationTypeResponse(BaseModel):
    """Ответ с описанием типа уведомления."""

    model_config = ConfigDict(from_attributes=True)

    type: str = Field(..., description="Значение типа", examples=["task_assigned"])
    label: str = Field(..., description="Человекочитаемое название", examples=["Задача назначена"])
    default_channels: list[str] = Field(
        default_factory=list,
        description="Каналы по умолчанию",
        examples=[["in_app", "email"]],
    )
