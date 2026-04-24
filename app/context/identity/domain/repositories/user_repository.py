from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.aggregates.user import User


class UserRepository(RepositoryPort[User]):
    """
    Порт репозитория для агрегата User.

    Расширяет базовый RepositoryPort специфичными запросами
    для Identity BC.
    """

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """
        Найти пользователя по email.

        Аргументы:
            email: Email-адрес пользователя.

        Возвращает:
            Агрегат User или None, если не найден.
        """

    @abstractmethod
    async def get_by_role(self, role_id: Id) -> list[User]:
        """
        Найти пользователей по ID роли.

        Аргументы:
            role_id: ID роли.

        Возвращает:
            Список пользователей с указанной ролью.
        """

    @abstractmethod
    async def search(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[User]:
        """
        Поиск пользователей с опциональной фильтрацией.

        Аргументы:
            offset: Смещение для пагинации.
            limit: Максимальное количество записей.
            filters: Словарь фильтров {поле: значение}.

        Возвращает:
            Список пользователей.
        """
