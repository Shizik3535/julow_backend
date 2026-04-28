from __future__ import annotations

from typing import Any

from app.shared.application.base_dto import BaseDTO


class WebSocketMessage(BaseDTO):
    """
    Сообщение для отправки через WebSocket.

    Атрибуты:
        event_type: Тип события (например, "notification.created").
        payload: Данные события.
    """

    event_type: str
    payload: dict[str, Any]
