from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_role import WorkspaceRole


class WorkspaceRoleRepository(RepositoryPort[WorkspaceRole]):
    """
    Порт репозитория для агрегата WorkspaceRole.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления ролями workspace.
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> WorkspaceRole | None:
        """Найти роль по названию."""

    @abstractmethod
    async def get_system_roles(self) -> list[WorkspaceRole]:
        """Получить все системные роли (is_system=True)."""

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[WorkspaceRole]:
        """Получить все роли workspace (системные + кастомные)."""

    @abstractmethod
    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[WorkspaceRole]:
        """Поиск ролей с опциональной фильтрацией."""
