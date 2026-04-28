from __future__ import annotations

from app.context.notification.application.ports.integration.outboard.reminder_window_provider import (
    ReminderWindowProvider,
)
from app.context.task.application.ports.integration.inboard.reminder_window_port import (
    ReminderWindowPort,
)


class ReminderWindowAdapter(ReminderWindowPort):
    """
    Реализация inboard-порта ReminderWindowPort для Task BC.

    Делегирует получение окна напоминания в outboard-порт
    Notification BC (ReminderWindowProvider).
    """

    def __init__(self, reminder_window_provider: ReminderWindowProvider) -> None:
        self._provider = reminder_window_provider

    async def get_reminder_window(self, user_id: str) -> int:
        return await self._provider.get_reminder_window(user_id=user_id)
