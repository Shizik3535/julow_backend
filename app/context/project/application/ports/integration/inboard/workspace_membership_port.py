from __future__ import annotations

from abc import ABC, abstractmethod


class WorkspaceMembershipPort(ABC):
    """
    Inboard-порт: проверка членства в workspace (ACL).

    Project BC использует этот порт для проверки, что пользователь
    является участником workspace, прежде чем добавить его в проект.
    Реализация — адаптер в infrastructure, делегирующий в
    WorkspaceMembershipProvider (outboard Workspace BC).
    """

    @abstractmethod
    async def is_workspace_member(self, workspace_id: str, user_id: str) -> bool:
        """Проверить, является ли пользователь участником workspace."""
