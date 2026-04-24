from __future__ import annotations

from abc import ABC, abstractmethod

from app.context.workspace.application.dto.workspace_dto import WorkspaceDTO


class WorkspaceProvider(ABC):
    """
    Outboard-порт: предоставление данных workspace другим BC.

    Реализуется в infrastructure слое Workspace BC.
    Другие BC инжектируют соответствующий inboard-порт,
    адаптер которого делегирует в этот provider.
    """

    @abstractmethod
    async def get_workspace(self, workspace_id: str) -> WorkspaceDTO | None:
        """Получить workspace по ID."""

    @abstractmethod
    async def workspace_exists(self, workspace_id: str) -> bool:
        """Проверить существование workspace."""

    @abstractmethod
    async def get_workspaces_by_organization(self, org_id: str) -> list[WorkspaceDTO]:
        """Получить все workspace организации."""
