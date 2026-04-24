from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.aggregates.role import Role


class RoleRepository(RepositoryPort[Role]):
    """
    Порт репозитория для агрегата Role.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления ролями.
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None:
        """
        Найти роль по названию.

        Аргументы:
            name: Название роли.

        Возвращает:
            Сущность Role или None, если не найдена.
        """

    @abstractmethod
    async def get_system_roles(self) -> list[Role]:
        """
        Получить все системные роли (is_system=True).

        Возвращает:
            Список системных ролей.
        """

    @abstractmethod
    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[Role]:
        """
        Поиск ролей с опциональной фильтрацией.

        Аргументы:
            offset: Смещение для пагинации.
            limit: Максимальное количество записей.
            filters: Словарь фильтров {поле: значение}.

        Возвращает:
            Список ролей.
        """
