from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.domain.aggregates.chat import Chat
from app.context.communication.domain.value_objects.chat_type import ChatType


class ChatRepository(RepositoryPort[Chat]):
    """Порт репозитория для агрегата Chat."""

    @abstractmethod
    async def get_by_member(self, user_id: Id) -> list[Chat]:
        """Найти чаты по участнику."""

    @abstractmethod
    async def get_dm_between(self, user_a: Id, user_b: Id) -> Chat | None:
        """Найти DM между двумя пользователями."""

    @abstractmethod
    async def get_by_workspace(self, workspace_id: Id) -> list[Chat]:
        """Найти чаты workspace."""

    @abstractmethod
    async def get_by_type(self, chat_type: ChatType) -> list[Chat]:
        """Найти чаты по типу."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[Chat]:
        """Поиск чатов."""
