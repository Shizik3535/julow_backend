from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.communication.domain.value_objects.comment_target_type import CommentTargetType
from app.context.communication.domain.value_objects.reaction_emoji import ReactionEmoji
from app.context.communication.domain.entities.reaction import Reaction
from app.context.communication.domain.entities.attachment import Attachment
from app.context.communication.domain.events.comment_events import (
    CommentAdded,
    CommentUpdated,
    CommentDeleted,
    CommentReplied,
    CommentReactionAdded,
    CommentReactionRemoved,
)
from app.context.communication.domain.exceptions.comment_exceptions import (
    CommentDeletedException,
    CannotDeleteCommentException,
    CannotUpdateCommentException,
    DuplicateReactionException,
)


# Жёсткий потолок длины выжимки в `CommentAdded`. Чуть больше типичной
# UI-карточки уведомления, но не настолько большой, чтобы раздувать
# payload событий / WebSocket-пуш и хранилище. Подрезка по слову, без
# середины слова.
_EXCERPT_MAX_LEN = 200


def _build_excerpt(content: RichText | None) -> str:
    """
    Получить короткую выжимку текста комментария для использования в
    событиях/уведомлениях. Не парсим markdown/HTML — это работа UI;
    здесь нам нужен лишь компактный preview, чтобы уведомление было
    осмысленным (как минимум начало фразы).
    """
    if content is None:
        return ""
    text = (content.content or "").strip()
    if len(text) <= _EXCERPT_MAX_LEN:
        return text
    cut = text[:_EXCERPT_MAX_LEN]
    # Подрезка по последнему пробелу — чтобы не разрывать слово.
    last_space = cut.rfind(" ")
    if last_space > 40:
        cut = cut[:last_space]
    return cut.rstrip() + "…"


@dataclass
class Comment(AggregateRoot):
    """
    Корень агрегата комментария (Communication BC).

    Комментарии привязываются к CommentTargetType + target_id (opaque),
    что позволяет комментировать любые сущности из любых BC.

    Атрибуты:
        author_id: ID автора.
        target_type: Тип комментируемой сущности.
        target_id: Opaque ID сущности.
        content: Содержание (форматированный текст).
        parent_comment_id: ID родительского комментария (для ответов).
        attachments: Список вложений.
        reactions: Список реакций.
        is_pinned: Закреплён ли комментарий.
        is_system: Является ли системным.
        is_deleted: Удалён ли (soft delete).
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    author_id: Id = field(default_factory=Id.generate)
    target_type: CommentTargetType = CommentTargetType.TASK
    target_id: Id = field(default_factory=Id.generate)
    content: RichText | None = None
    parent_comment_id: Id | None = None
    attachments: list[Attachment] = field(default_factory=list)
    reactions: list[Reaction] = field(default_factory=list)
    is_pinned: bool = False
    is_system: bool = False
    is_deleted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        author_id: Id,
        target_type: CommentTargetType,
        target_id: Id,
        content: RichText | None,
        parent_comment_id: Id | None = None,
    ) -> Comment:
        """Создаёт комментарий."""
        comment = cls(
            author_id=author_id,
            target_type=target_type,
            target_id=target_id,
            content=content,
            parent_comment_id=parent_comment_id,
        )
        event_cls = CommentReplied if parent_comment_id else CommentAdded
        if parent_comment_id:
            comment._register_event(
                CommentReplied(
                    comment_id=str(comment.id),
                    parent_comment_id=str(parent_comment_id),
                )
            )
        else:
            comment._register_event(
                CommentAdded(
                    comment_id=str(comment.id),
                    target_type=target_type,
                    target_id=str(target_id),
                    author_id=str(author_id),
                    content_excerpt=_build_excerpt(content),
                )
            )
        return comment

    @classmethod
    def create_system(
        cls,
        target_type: CommentTargetType,
        target_id: Id,
        content: RichText | None,
    ) -> Comment:
        """Создаёт системный комментарий."""
        comment = cls(
            target_type=target_type,
            target_id=target_id,
            content=content,
            is_system=True,
        )
        comment._register_event(
            CommentAdded(
                comment_id=str(comment.id),
                target_type=target_type,
                target_id=str(target_id),
                author_id="",
                content_excerpt=_build_excerpt(content),
            )
        )
        return comment

    def update(self, content: RichText | None) -> None:
        """Обновляет содержание комментария."""
        if self.is_system:
            raise CannotUpdateCommentException(reason="системный")
        if self.is_deleted:
            raise CannotUpdateCommentException(reason="удалённый")
        self.content = content
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(CommentUpdated(comment_id=str(self.id)))

    def delete(self) -> None:
        """Soft delete комментария."""
        if self.is_system:
            raise CannotDeleteCommentException()
        if self.is_deleted:
            return
        self.is_deleted = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(CommentDeleted(comment_id=str(self.id)))

    def pin(self) -> None:
        self.is_pinned = True
        self.updated_at = datetime.now(tz=timezone.utc)

    def unpin(self) -> None:
        self.is_pinned = False
        self.updated_at = datetime.now(tz=timezone.utc)

    def add_reaction(self, user_id: Id, emoji: ReactionEmoji) -> None:
        if any(r.user_id == user_id and r.emoji == emoji for r in self.reactions):
            raise DuplicateReactionException()
        reaction = Reaction(user_id=user_id, emoji=emoji)
        self.reactions.append(reaction)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            CommentReactionAdded(
                comment_id=str(self.id), user_id=str(user_id), emoji=str(emoji)
            )
        )

    def remove_reaction(self, user_id: Id, emoji: ReactionEmoji) -> None:
        self.reactions = [
            r for r in self.reactions
            if not (r.user_id == user_id and r.emoji == emoji)
        ]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            CommentReactionRemoved(
                comment_id=str(self.id), user_id=str(user_id), emoji=str(emoji)
            )
        )

    def add_attachment(self, attachment: Attachment) -> None:
        self.attachments.append(attachment)
        self.updated_at = datetime.now(tz=timezone.utc)

    def remove_attachment(self, attachment_id: Id) -> None:
        self.attachments = [a for a in self.attachments if a.id != attachment_id]
        self.updated_at = datetime.now(tz=timezone.utc)
