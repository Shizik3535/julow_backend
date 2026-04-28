from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SetNotificationPreferenceRequest(BaseModel):
    """
    Тело запроса установки настройки уведомлений.

    Атрибуты:
        notification_type: Тип уведомления.
        channel: Канал доставки.
        enabled: Включён ли канал.
        scope: Область действия (global/project/workspace).
        scope_id: ID проекта или workspace.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notification_type": "task_assigned",
                "channel": "in_app",
                "enabled": True,
                "scope": "global",
            },
        },
    )

    notification_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Тип уведомления",
        examples=["task_assigned"],
    )
    channel: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Канал доставки (in_app/email/push)",
        examples=["in_app"],
    )
    enabled: bool = Field(
        default=True,
        description="Включён ли канал",
    )
    scope: str = Field(
        default="global",
        description="Область действия (global/project/workspace)",
        examples=["global"],
    )
    scope_id: str | None = Field(
        default=None,
        description="ID проекта или workspace (если scope не global)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
