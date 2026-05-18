from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.project.domain.aggregates.project_invitation import ProjectInvitation


class ProjectInvitationRepository(RepositoryPort[ProjectInvitation]):
    """
    Порт репозитория для агрегата ProjectInvitation.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления приглашениями в проект.
    """

    @abstractmethod
    async def get_by_project_id(self, project_id: Id) -> list[ProjectInvitation]:
        """Получить все приглашения проекта."""

    @abstractmethod
    async def get_by_token(self, token_value: str) -> ProjectInvitation | None:
        """Найти приглашение по значению токена ссылки/кода."""

    @abstractmethod
    async def get_pending_by_project(self, project_id: Id) -> list[ProjectInvitation]:
        """Получить все ожидающие приглашения проекта."""

    @abstractmethod
    async def search_by_user(
        self,
        email: str,
        user_id: Id | None = None,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[ProjectInvitation], int]:
        """
        Поиск приглашений пользователя.

        Ищет по (email + PENDING) или по user_id.
        Возвращает (список приглашений, общее количество).
        """
