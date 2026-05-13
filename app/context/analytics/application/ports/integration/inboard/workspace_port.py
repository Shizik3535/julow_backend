from __future__ import annotations

from abc import ABC, abstractmethod


class WorkspacePort(ABC):
    """Inboard-порт: проверки workspace из Workspace BC."""

    @abstractmethod
    async def workspace_exists(self, workspace_id: str) -> bool:
        """Проверить существование workspace."""

    @abstractmethod
    async def is_member(self, workspace_id: str, user_id: str) -> bool:
        """Проверить членство пользователя в workspace."""
