from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.shared.domain.base_repository import RepositoryPort
from app.shared.domain.value_objects.id_vo import Id
from app.context.communication.domain.aggregates.comment import Comment
from app.context.communication.domain.value_objects.comment_target_type import CommentTargetType


class CommentRepository(RepositoryPort[Comment]):
    """Порт репозитория для агрегата Comment."""

    @abstractmethod
    async def get_by_target(self, target_id: Id) -> list[Comment]:
        """Найти комментарии по ID цели."""

    @abstractmethod
    async def get_by_target_and_type(self, target_id: Id, target_type: CommentTargetType) -> list[Comment]:
        """Найти комментарии по цели и типу."""

    @abstractmethod
    async def get_replies(self, parent_comment_id: Id) -> list[Comment]:
        """Найти ответы на комментарий."""

    @abstractmethod
    async def get_by_author(self, author_id: Id) -> list[Comment]:
        """Найти комментарии автора."""

    @abstractmethod
    async def search(self, offset: int = 0, limit: int = 100, filters: dict[str, Any] | None = None) -> list[Comment]:
        """Поиск комментариев."""

    @abstractmethod
    async def count_by_target(self, target_id: Id) -> int:
        """Подсчитать комментарии к цели."""
