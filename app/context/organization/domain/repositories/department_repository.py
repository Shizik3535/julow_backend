from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.department import Department


class DepartmentRepository(RepositoryPort[Department]):
    """
    Порт репозитория для агрегата Department.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления подразделениями.
    """

    @abstractmethod
    async def get_by_org_id(self, org_id: Id) -> list[Department]:
        """Получить все подразделения организации."""

    @abstractmethod
    async def get_by_parent(self, parent_id: Id) -> list[Department]:
        """Получить дочерние подразделения."""

    @abstractmethod
    async def get_by_member(self, user_id: Id) -> list[Department]:
        """Получить подразделения, в которых состоит пользователь."""
