from __future__ import annotations

from abc import ABC, abstractmethod


class ProjectMembershipPort(ABC):
    """
    Inboard-порт: проверка участия пользователя в проекте (Project BC).

    Используется для ACL-проверок при назначении исполнителей.
    """

    @abstractmethod
    async def is_project_member(self, project_id: str, user_id: str) -> bool:
        """Проверить, является ли пользователь участником проекта."""
