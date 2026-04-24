from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.aggregates.session import Session
from app.context.identity.domain.value_objects.refresh_token import RefreshToken


class SessionRepository(RepositoryPort[Session]):
    """
    Порт репозитория для агрегата Session.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления сессиями.
    """

    @abstractmethod
    async def get_active_by_user(self, user_id: Id) -> list[Session]:
        """
        Получить все активные сессии пользователя.

        Аргументы:
            user_id: ID пользователя.

        Возвращает:
            Список активных сессий.
        """

    @abstractmethod
    async def get_by_user(self, user_id: Id) -> list[Session]:
        """
        Получить все сессии пользователя (включая завершённые).

        Аргументы:
            user_id: ID пользователя.

        Возвращает:
            Список всех сессий пользователя.
        """

    @abstractmethod
    async def count_active_by_user(self, user_id: Id) -> int:
        """
        Посчитать количество активных сессий пользователя.

        Аргументы:
            user_id: ID пользователя.

        Возвращает:
            Количество активных сессий.
        """

    @abstractmethod
    async def get_by_refresh_token(self, token: RefreshToken) -> Session | None:
        """
        Найти сессию по refresh-токену.

        Аргументы:
            token: Refresh-токен.

        Возвращает:
            Агрегат Session или None, если не найден.
        """

    @abstractmethod
    async def terminate_all_by_user(
        self, user_id: Id, except_session_id: Id | None = None
    ) -> int:
        """
        Завершить все сессии пользователя, кроме указанной.

        Аргументы:
            user_id: ID пользователя.
            except_session_id: ID сессии, которую не нужно завершать (текущая).

        Возвращает:
            Количество завершённых сессий.
        """

    @abstractmethod
    async def terminate_by_user(self, user_id: Id, session_id: Id) -> bool:
        """
        Завершить конкретную сессию пользователя.

        Аргументы:
            user_id: ID пользователя (для проверки принадлежности).
            session_id: ID сессии для завершения.

        Возвращает:
            True, если сессия была найдена и завершена.
        """
