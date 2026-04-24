from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChannelPreferenceInput(BaseModel):
    """
    Настройка канала доставки уведомления.

    Атрибуты:
        channel: Канал (in_app, email, push, sms).
        is_enabled: Включён ли канал.
    """

    channel: str = Field(
        ...,
        description="Канал доставки (in_app, email, push, sms)",
        examples=["email"],
    )
    is_enabled: bool = Field(
        default=True,
        description="Включён ли канал",
    )


class TypePreferenceInput(BaseModel):
    """
    Настройка типа уведомления.

    Атрибуты:
        notification_type: Тип уведомления (task_assigned, mention и т.д.).
        is_enabled: Включён ли тип целиком.
        channels: Список настроек каналов для данного типа.
    """

    notification_type: str = Field(
        ...,
        description="Тип уведомления (task_assigned, task_updated, mention, comment_added, ...)",
        examples=["task_assigned"],
    )
    is_enabled: bool = Field(
        default=True,
        description="Включён ли данный тип уведомления",
    )
    channels: list[ChannelPreferenceInput] = Field(
        default_factory=list,
        description="Настройки каналов доставки для данного типа",
    )


class UpdateNotificationsRequest(BaseModel):
    """
    Тело запроса обновления настроек уведомлений.

    Атрибуты:
        type_preferences: Список настроек по типам уведомлений.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type_preferences": [
                    {
                        "notification_type": "task_assigned",
                        "is_enabled": True,
                        "channels": [
                            {"channel": "in_app", "is_enabled": True},
                            {"channel": "email", "is_enabled": True},
                            {"channel": "push", "is_enabled": False},
                            {"channel": "sms", "is_enabled": False},
                        ],
                    },
                ],
            },
        },
    )

    type_preferences: list[TypePreferenceInput] = Field(
        ...,
        description="Список настроек по типам уведомлений",
    )
