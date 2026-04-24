from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.org_membership import OrgMembership
from app.context.organization.domain.entities.org_member import OrgMember


class OrgMembershipRepository(RepositoryPort[OrgMembership]):
    """
    Порт репозитория для агрегата OrgMembership.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления участниками организации.
    """

    @abstractmethod
    async def get_by_org_id(self, org_id: Id) -> OrgMembership | None:
        """Найти членство по ID организации."""

    @abstractmethod
    async def get_member_by_org_and_user(self, org_id: Id, user_id: Id) -> OrgMember | None:
        """Найти участника по org_id и user_id."""

    @abstractmethod
    async def get_members_by_org(self, org_id: Id) -> list[OrgMember]:
        """Получить всех участников организации."""
