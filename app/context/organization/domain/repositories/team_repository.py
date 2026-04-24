from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.team import Team


class TeamRepository(RepositoryPort[Team]):
    """
    Порт репозитория для агрегата Team.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления командами.
    """

    @abstractmethod
    async def get_by_org(self, org_id: Id) -> list[Team]:
        """Найти все команды организации."""

    @abstractmethod
    async def get_by_member(self, user_id: Id) -> list[Team]:
        """Найти команды по ID участника."""

    @abstractmethod
    async def get_by_lead(self, user_id: Id) -> list[Team]:
        """Найти команды по ID лидера."""
