from __future__ import annotations

from abc import ABC, abstractmethod


class ProjectMemberPort(ABC):
    """
    Inboard-порт: получение участников проекта из Project BC.

    Notification BC использует для определения получателей уведомлений
    при событии ProjectDeadlineApproaching.
    """

    @abstractmethod
    async def get_project_members(self, project_id: str) -> list[str]:
        """Вернуть список user_id участников проекта (members + owners, unique)."""
