from __future__ import annotations

from typing import Any
from uuid import UUID

from app.shared.application.base_dto import BaseDTO


class PushMessage(BaseDTO):
    """
    Push-уведомление.

    Атрибуты:
        recipient_id: Идентификатор получателя.
        title: Заголовок уведомления.
        body: Тело уведомления.
        data: Дополнительные данные (deep link и т.д.).
    """

    recipient_id: UUID
    title: str
    body: str
    data: dict[str, Any] | None = None
