from __future__ import annotations

from abc import ABC, abstractmethod


class TaskParticipantPort(ABC):
    """
    Inboard-порт: получение участников задачи из Task BC.

    Notification BC использует для определения получателей уведомлений
    при событиях TaskStatusChanged, TaskCommentAdded и т.д.
    """

    @abstractmethod
    async def get_task_participants(self, task_id: str) -> list[str]:
        """Вернуть список user_id участников задачи (assignees + watchers + reporter, unique)."""

    @abstractmethod
    async def get_task_assignees(self, task_id: str) -> list[str]:
        """Вернуть список user_id исполнителей задачи."""
