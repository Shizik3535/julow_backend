from __future__ import annotations

from abc import ABC, abstractmethod


class TaskParticipantProvider(ABC):
    """
    Outboard-порт: предоставление данных участников задачи другим BC.

    Реализуется в infrastructure слое Task BC.
    Notification BC и другие инжектируют inboard-порт,
    адаптер которого делегирует в этот provider.
    """

    @abstractmethod
    async def get_task_participants(self, task_id: str) -> list[str]:
        """Вернуть список user_id участников задачи (assignees + watchers + reporter, unique)."""

    @abstractmethod
    async def get_task_assignees(self, task_id: str) -> list[str]:
        """Вернуть список user_id исполнителей задачи."""
