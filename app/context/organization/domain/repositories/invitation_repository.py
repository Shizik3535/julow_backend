from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.organization.domain.aggregates.invitation import Invitation


class InvitationRepository(RepositoryPort[Invitation]):
    """
    Порт репозитория для агрегата Invitation.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления приглашениями.
    """

    @abstractmethod
    async def get_by_org_id(self, org_id: Id) -> list[Invitation]:
        """Получить все приглашения организации."""

    @abstractmethod
    async def get_by_token(self, token_value: str) -> Invitation | None:
        """Найти приглашение по значению токена ссылки."""

    @abstractmethod
    async def get_pending_by_org(self, org_id: Id) -> list[Invitation]:
        """Получить все ожидающие приглашения организации."""

    @abstractmethod
    async def search_by_user(
        self,
        email: str,
        user_id: Id | None = None,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[Invitation], int]:
        """
        Поиск приглашений пользователя.

        Ищет по (email + PENDING) или по user_id.
        Возвращает (список приглашений, общее количество).
        """
