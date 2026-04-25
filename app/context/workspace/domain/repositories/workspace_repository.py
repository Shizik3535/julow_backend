from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace import Workspace


class WorkspaceRepository(RepositoryPort[Workspace]):
    """
    Порт репозитория для агрегата Workspace.

    Расширяет базовый RepositoryPort специфичными запросами
    для Workspace BC.
    """

    @abstractmethod
    async def get_by_owner(self, owner_id: Id) -> list[Workspace]:
        """Найти workspace по ID владельца."""

    @abstractmethod
    async def get_by_organization(self, organization_id: Id) -> list[Workspace]:
        """Найти workspace по ID организации."""

    @abstractmethod
    async def get_by_organization_and_member(
        self, organization_id: Id, user_id: Id
    ) -> list[Workspace]:
        """
        Найти workspace организации, в которых пользователь является участником.

        Используется для фильтрации выдачи, когда у caller'а нет орг-разрешения
        `workspaces.read` — возвращаются только те workspace, где он присутствует
        в WorkspaceMembership.
        """

    @abstractmethod
    async def get_by_parent(self, parent_workspace_id: Id) -> list[Workspace]:
        """Найти дочерние workspace по ID родителя."""

    @abstractmethod
    async def get_children(self, workspace_id: Id) -> list[Workspace]:
        """Получить все дочерние workspace."""

    @abstractmethod
    async def get_root_workspaces(self) -> list[Workspace]:
        """Получить все корневые workspace (без родителя)."""

    @abstractmethod
    async def get_by_member(self, user_id: Id) -> list[Workspace]:
        """Найти все workspace, в которых пользователь является участником."""

    @abstractmethod
    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Workspace]:
        """Поиск workspace с фильтрацией."""

    @abstractmethod
    async def count_by_organization(self, organization_id: Id) -> int:
        """Подсчитать количество workspace в организации."""
