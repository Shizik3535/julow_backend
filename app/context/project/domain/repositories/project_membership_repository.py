from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project_membership import ProjectMembership
from app.context.project.domain.entities.project_member import ProjectMember


class ProjectMembershipRepository(RepositoryPort[ProjectMembership]):
    """Порт репозитория для агрегата ProjectMembership."""

    @abstractmethod
    async def get_by_project_id(self, project_id: Id) -> ProjectMembership | None:
        """Найти членство по ID проекта."""

    @abstractmethod
    async def get_member_by_project_and_user(self, project_id: Id, user_id: Id) -> ProjectMember | None:
        """Найти участника по project_id и user_id."""

    @abstractmethod
    async def get_members_by_project(self, project_id: Id) -> list[ProjectMember]:
        """Получить всех участников проекта."""
