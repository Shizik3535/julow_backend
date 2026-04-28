from __future__ import annotations

from abc import ABC, abstractmethod


class ReminderWindowPort(ABC):
    """
    Inboard-порт: получение окна напоминания пользователя из Notification BC.

    Project BC использует для определения за сколько часов до дедлайна
    отправлять напоминание конкретному пользователю.
    """

    @abstractmethod
    async def get_reminder_window(self, user_id: str) -> int:
        """Вернуть окно напоминания в часах (default=24)."""
