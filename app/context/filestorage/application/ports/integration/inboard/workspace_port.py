from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class WorkspacePort(ABC):
    """
    Inboard-порт: получение данных workspace из Workspace BC.

    FileStorage BC использует его для проверки существования workspace
    при создании файлов/папок/хранилищ.
    """

    @abstractmethod
    async def workspace_exists(self, workspace_id: str) -> bool:
        """Проверить существование workspace."""

    @abstractmethod
    async def get_workspace(self, workspace_id: str) -> dict[str, Any] | None:
        """Получить данные workspace (dict) или None."""
