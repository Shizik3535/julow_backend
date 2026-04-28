from __future__ import annotations

from datetime import datetime
from typing import Any

from app.shared.application.base_dto import BaseDTO


class NotificationDTO(BaseDTO):
    """
    DTO уведомления (Notification BC).

    Атрибуты:
        id: Идентификатор.
        recipient_id: ID получателя.
        workspace_id: ID workspace.
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
        created_at: Время создания.
    """

    id: str
    recipient_id: str
    workspace_id: str | None = None
    notification_type: str = ""
    title: str = ""
    body: str = ""
    priority: str = "normal"
    data: dict[str, Any] = {}
    channels: list[str] = []
    is_read: bool = False
    read_at: datetime | None = None
    is_archived: bool = False
    actor_id: str | None = None
    created_at: datetime | None = None
