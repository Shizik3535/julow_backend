from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_membership import WorkspaceMembership
from app.context.workspace.domain.entities.workspace_member import WorkspaceMember


class WorkspaceMembershipRepository(RepositoryPort[WorkspaceMembership]):
    """
    Порт репозитория для агрегата WorkspaceMembership.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления участниками workspace.
    """

    @abstractmethod
    async def get_by_workspace_id(self, workspace_id: Id) -> WorkspaceMembership | None:
        """Найти членство по ID workspace."""

    @abstractmethod
    async def get_member_by_workspace_and_user(self, workspace_id: Id, user_id: Id) -> WorkspaceMember | None:
        """Найти участника по workspace_id и user_id."""

    @abstractmethod
    async def get_members_by_workspace(self, workspace_id: Id) -> list[WorkspaceMember]:
        """Получить всех участников workspace."""
