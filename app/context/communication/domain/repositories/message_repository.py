from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.domain.aggregates.message import Message


class MessageRepository(RepositoryPort[Message]):
    """Порт репозитория для агрегата Message."""

    @abstractmethod
    async def get_by_chat(self, chat_id: Id, offset: int = 0, limit: int = 50) -> list[Message]:
        """Получить сообщения чата с пагинацией."""

    @abstractmethod
    async def get_by_thread(self, thread_id: Id) -> list[Message]:
        """Получить сообщения треда."""

    @abstractmethod
    async def get_by_chat_after(self, chat_id: Id, after: datetime) -> list[Message]:
        """Получить сообщения чата после указанного времени (real-time)."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[Message]:
        """Поиск сообщений."""

    @abstractmethod
    async def count_unread(self, chat_id: Id, after: datetime) -> int:
        """Подсчитать непрочитанные сообщения."""
