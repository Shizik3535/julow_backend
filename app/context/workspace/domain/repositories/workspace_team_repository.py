from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_team import WorkspaceTeam


class WorkspaceTeamRepository(RepositoryPort[WorkspaceTeam]):
    """
    Порт репозитория для агрегата WorkspaceTeam.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления командами workspace.
    """

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[WorkspaceTeam]:
        """Найти все команды workspace."""

    @abstractmethod
    async def get_by_member(self, user_id: Id) -> list[WorkspaceTeam]:
        """Найти команды по ID участника."""

    @abstractmethod
    async def get_by_lead(self, user_id: Id) -> list[WorkspaceTeam]:
        """Найти команды по ID лидера."""
