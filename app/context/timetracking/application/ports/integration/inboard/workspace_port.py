from __future__ import annotations

from abc import ABC, abstractmethod


class WorkspacePort(ABC):
    """
    Inboard-порт: получение данных workspace из Workspace BC.

    TimeTracking BC использует его для проверки существования workspace
    и членства пользователя.
    """

    @abstractmethod
    async def workspace_exists(self, workspace_id: str) -> bool:
        """Проверить существование workspace."""

    @abstractmethod
    async def is_member(self, workspace_id: str, user_id: str) -> bool:
        """Проверить членство пользователя в workspace."""
