from __future__ import annotations

from abc import abstractmethod

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.email_vo import Email
from app.shared.domain.value_objects.id_vo import Id
from app.context.identity.domain.aggregates.user_auth import UserAuth
from app.context.identity.domain.value_objects.auth_provider import AuthProvider


class UserAuthRepository(RepositoryPort[UserAuth]):
    """
    Порт репозитория для агрегата UserAuth.

    Расширяет базовый RepositoryPort специфичными запросами
    для аутентификации.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: Id) -> UserAuth | None:
        """
        Найти UserAuth по ID пользователя.

        Аргументы:
            user_id: ID пользователя (opaque ID из агрегата User).

        Возвращает:
            Агрегат UserAuth или None, если не найден.
        """

    @abstractmethod
    async def get_by_email(self, email: Email) -> UserAuth | None:
        """
        Найти UserAuth по email.

        Аргументы:
            email: Email-адрес пользователя.

        Возвращает:
            Агрегат UserAuth или None, если не найден.
        """

    @abstractmethod
    async def get_by_oauth_provider(
        self, provider: AuthProvider, provider_user_id: str
    ) -> UserAuth | None:
        """
        Найти UserAuth по OAuth-провайдеру и ID у провайдера.

        Аргументы:
            provider: Тип провайдера аутентификации.
            provider_user_id: ID пользователя у провайдера.

        Возвращает:
            Агрегат UserAuth или None, если не найден.
        """
