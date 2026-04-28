from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class NotificationSenderPort(ABC):
    """
    BC-специфичный порт для отправки уведомлений по каналам.

    Реализация в infrastructure-слое оркестрирует:
    - In-app: через WebSocket
    - Email: через shared EmailPort
    - Push: через shared PushPort
    """

    @abstractmethod
    async def send_notification(
        self,
        recipient_id: str,
        notification_type: str,
        title: str,
        body: str,
        data: dict[str, Any],
        channels: list[str],
        priority: str = "normal",
    ) -> None:
        """Отправить уведомление по указанным каналам."""
