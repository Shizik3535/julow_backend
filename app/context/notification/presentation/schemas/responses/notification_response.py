from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    """
    Ответ с данными уведомления.

    Атрибуты:
        id: UUID уведомления.
        recipient_id: UUID получателя.
        workspace_id: UUID workspace.
        notification_type: Тип уведомления.
        title: Заголовок.
        body: Тело.
        priority: Приоритет.
        data: Контекстные данные.
        channels: Каналы доставки.
        is_read: Прочитано ли.
        read_at: Время прочтения.
        is_archived: Архивировано ли.
        actor_id: ID инициатора.
        created_at: Дата создания.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="UUID уведомления",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    recipient_id: str = Field(
        ...,
        description="UUID получателя",
        examples=["550e8400-e29b-41d4-a716-446655440001"],
    )
    workspace_id: str | None = Field(
        default=None,
        description="UUID workspace",
        examples=["550e8400-e29b-41d4-a716-446655440002"],
    )
    notification_type: str = Field(
        ...,
        description="Тип уведомления",
        examples=["task_assigned"],
    )
    title: str = Field(..., description="Заголовок", examples=["Вам назначена задача"])
    body: str = Field(..., description="Тело уведомления", examples=["Задача X назначена на вас"])
    priority: str = Field(default="normal", description="Приоритет", examples=["normal"])
    data: dict[str, Any] = Field(default_factory=dict, description="Контекстные данные")
    channels: list[str] = Field(default_factory=list, description="Каналы доставки", examples=[["in_app"]])
    is_read: bool = Field(default=False, description="Прочитано ли")
    read_at: datetime | None = Field(default=None, description="Время прочтения (UTC)")
    is_archived: bool = Field(default=False, description="Архивировано ли")
    actor_id: str | None = Field(default=None, description="UUID инициатора")
    created_at: datetime | None = Field(default=None, description="Дата создания (UTC)")
