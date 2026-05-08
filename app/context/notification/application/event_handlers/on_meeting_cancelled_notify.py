"""Обработчик события ``MeetingCancelled`` (Communication BC).

Шлёт уведомление об отмене. В MVP — упрощённый вариант (text-only);
расширять рассылку участникам можно позже через дополнительный запрос
в Communication BC.
"""

from __future__ import annotations

from typing import Any

from app.shared.application.base_event_handler import BaseEventHandler
from app.shared.application.messaging.domain_event_bus import DomainEventBus
from app.context.notification.domain.repositories.notification_repository import (
    NotificationRepository,
)


class OnMeetingCancelledNotify(BaseEventHandler[dict[str, Any]]):
    """Placeholder-handler для события ``MeetingCancelled``.

    В MVP не рассылает уведомления (нужен meeting.participants, за которыми
    надо ходить в Communication BC — это требует ``MeetingProvider`` outboard-порта).
    Заглушка оставлена для дальнейшего расширения.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
        event_bus: DomainEventBus,
    ) -> None:
        super().__init__()
        self._repo = notification_repo
        self._event_bus = event_bus

    async def handle(self, event: dict[str, Any]) -> None:
        if event.get("event_type") != "MeetingCancelled":
            return
        return None
