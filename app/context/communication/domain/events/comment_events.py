from __future__ import annotations

from dataclasses import dataclass

from app.shared.domain.base_domain_event import BaseDomainEvent
from app.context.communication.domain.value_objects.comment_target_type import CommentTargetType


@dataclass(frozen=True)
class CommentAdded(BaseDomainEvent):
    """
    Комментарий добавлен.

    Атрибуты:
        comment_id: ID нового комментария.
        target_type: Тип сущности, к которой относится комментарий (task/project/…).
        target_id: ID целевой сущности.
        author_id: ID автора (пустая строка для системных).
        content_excerpt: Краткая текстовая выжимка содержимого (первые
            ~200 символов plain text). Используется потребителями события
            (например, `OnCommentAddedNotify`), чтобы построить уведомление
            с реальным текстом комментария — без необходимости позднее
            загружать сам Comment-агрегат.
    """

    comment_id: str = ""
    target_type: CommentTargetType = CommentTargetType.TASK
    target_id: str = ""
    author_id: str = ""
    content_excerpt: str = ""


@dataclass(frozen=True)
class CommentUpdated(BaseDomainEvent):
    """Комментарий обновлён."""

    comment_id: str = ""


@dataclass(frozen=True)
class CommentDeleted(BaseDomainEvent):
    """Комментарий удалён (soft)."""

    comment_id: str = ""


@dataclass(frozen=True)
class CommentReplied(BaseDomainEvent):
    """Ответ на комментарий."""

    comment_id: str = ""
    parent_comment_id: str = ""


@dataclass(frozen=True)
class CommentReactionAdded(BaseDomainEvent):
    """Реакция на комментарий."""

    comment_id: str = ""
    user_id: str = ""
    emoji: str = ""


@dataclass(frozen=True)
class CommentReactionRemoved(BaseDomainEvent):
    """Реакция на комментарий снята."""

    comment_id: str = ""
    user_id: str = ""
    emoji: str = ""


@dataclass(frozen=True)
class UserMentioned(BaseDomainEvent):
    """Пользователь упомянут."""

    mentioned_user_id: str = ""
    source_type: CommentTargetType = CommentTargetType.TASK
    source_id: str = ""
