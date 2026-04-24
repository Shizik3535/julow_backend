from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class WorkspacePort(ABC):
    """
    Inboard-порт: получение данных workspace из Workspace BC.

    Project BC использует этот порт для проверки существования
    workspace при создании проекта.
    Реализация — адаптер в infrastructure, делегирующий в
    WorkspaceProvider (outboard Workspace BC).
    """

    @abstractmethod
    async def workspace_exists(self, workspace_id: str) -> bool:
        """Проверить существование workspace."""

    @abstractmethod
    async def get_workspace(self, workspace_id: str) -> dict[str, Any] | None:
        """Получить данные workspace (dict) или None."""
