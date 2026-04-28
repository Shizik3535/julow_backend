from __future__ import annotations

from abc import ABC, abstractmethod


class ReminderWindowProvider(ABC):
    """
    Outboard-порт: предоставление данных об окне напоминания другим BC.

    Реализуется в infrastructure слое Notification BC.
    Task BC инжектирует inboard-порт, адаптер которого делегирует в этот provider.
    """

    @abstractmethod
    async def get_reminder_window(self, user_id: str) -> int:
        """Вернуть окно напоминания в часах (default=24)."""
