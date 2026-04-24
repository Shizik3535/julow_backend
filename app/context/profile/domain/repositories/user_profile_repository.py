from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.profile.domain.aggregates.user_profile import UserProfile


class UserProfileRepository(RepositoryPort[UserProfile]):
    """
    Порт репозитория для агрегата UserProfile.

    Расширяет базовый RepositoryPort специфичными запросами
    для Profile BC.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: Id) -> UserProfile | None:
        """
        Найти профиль по user_id (opaque ID из Identity BC).

        Аргументы:
            user_id: ID пользователя из Identity BC.

        Возвращает:
            Агрегат UserProfile или None, если не найден.
        """

    @abstractmethod
    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[UserProfile]:
        """
        Поиск профилей с опциональной фильтрацией.

        Аргументы:
            offset: Смещение для пагинации.
            limit: Максимальное количество записей.
            filters: Словарь фильтров {поле: значение}.

        Возвращает:
            Список профилей.
        """

    @abstractmethod
    async def get_by_role(self, role_id: Id) -> list[UserProfile]:
        """
        Найти профили пользователей с указанной ролью (для administration).

        Аргументы:
            role_id: ID роли.

        Возвращает:
            Список профилей пользователей с указанной ролью.
        """
