from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.workspace.domain.aggregates.workspace_invitation import WorkspaceInvitation


class WorkspaceInvitationRepository(RepositoryPort[WorkspaceInvitation]):
    """
    Порт репозитория для агрегата WorkspaceInvitation.

    Расширяет базовый RepositoryPort специфичными запросами
    для управления приглашениями в workspace.
    """

    @abstractmethod
    async def get_by_workspace_id(self, workspace_id: Id) -> list[WorkspaceInvitation]:
        """Получить все приглашения workspace."""

    @abstractmethod
    async def get_by_token(self, token_value: str) -> WorkspaceInvitation | None:
        """Найти приглашение по значению токена ссылки."""

    @abstractmethod
    async def get_pending_by_workspace(self, workspace_id: Id) -> list[WorkspaceInvitation]:
        """Получить все ожидающие приглашения workspace."""

    @abstractmethod
    async def search_by_user(
        self,
        email: str,
        user_id: Id | None = None,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[WorkspaceInvitation], int]:
        """
        Поиск приглашений пользователя.

        Ищет по (email + PENDING) или по user_id.
        Возвращает (список приглашений, общее количество).
        """
