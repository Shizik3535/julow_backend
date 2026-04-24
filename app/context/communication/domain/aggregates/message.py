from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_aggregate import AggregateRoot
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.context.communication.domain.value_objects.message_type import MessageType
from app.context.communication.domain.value_objects.reaction_emoji import ReactionEmoji
from app.context.communication.domain.entities.reaction import Reaction
from app.context.communication.domain.entities.attachment import Attachment
from app.context.communication.domain.events.message_events import (
    MessageSent,
    MessageUpdated,
    MessageDeleted,
    MessageReactionAdded,
    MessageReactionRemoved,
)
from app.context.communication.domain.exceptions.comment_exceptions import (
    DuplicateReactionException,
)


@dataclass
class Message(AggregateRoot):
    """
    Корень агрегата сообщения (Communication BC).

    Отдельный AR — не загружается в Chat. Доступ через MessageRepository
    с пагинацией.

    Атрибуты:
        chat_id: Opaque ID чата.
        thread_id: Opaque ID треда (None — основной чат).
        sender_id: ID отправителя.
        content: Содержание (форматированный текст).
        message_type: Тип сообщения.
        attachments: Список вложений.
        reactions: Список реакций.
        is_edited: Было ли отредактировано.
        is_deleted: Удалено ли (soft delete).
        reply_to_id: ID сообщения-ответа.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    chat_id: Id = field(default_factory=Id.generate)
    thread_id: Id | None = None
    sender_id: Id = field(default_factory=Id.generate)
    content: RichText | None = None
    message_type: MessageType = MessageType.TEXT
    attachments: list[Attachment] = field(default_factory=list)
    reactions: list[Reaction] = field(default_factory=list)
    is_edited: bool = False
    is_deleted: bool = False
    reply_to_id: Id | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @classmethod
    def create(
        cls,
        chat_id: Id,
        sender_id: Id,
        content: RichText | None,
        message_type: MessageType = MessageType.TEXT,
        thread_id: Id | None = None,
        reply_to_id: Id | None = None,
    ) -> Message:
        """Создаёт сообщение."""
        message = cls(
            chat_id=chat_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
            thread_id=thread_id,
            reply_to_id=reply_to_id,
        )
        message._register_event(
            MessageSent(
                message_id=str(message.id),
                chat_id=str(chat_id),
                sender_id=str(sender_id),
                message_type=message_type,
            )
        )
        return message

    @classmethod
    def create_system(cls, chat_id: Id, content: RichText | None) -> Message:
        """Создаёт системное сообщение."""
        message = cls(
            chat_id=chat_id,
            content=content,
            message_type=MessageType.SYSTEM,
        )
        message._register_event(
            MessageSent(
                message_id=str(message.id),
                chat_id=str(chat_id),
                sender_id="",
                message_type=MessageType.SYSTEM,
            )
        )
        return message

    def update(self, content: RichText | None) -> None:
        """Обновляет содержание сообщения."""
        if self.is_deleted:
            raise ValueError("Нельзя редактировать удалённое сообщение")
        if self.message_type == MessageType.SYSTEM:
            raise ValueError("Нельзя редактировать системное сообщение")
        self.content = content
        self.is_edited = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(MessageUpdated(message_id=str(self.id)))

    def delete(self) -> None:
        """Soft delete сообщения."""
        if self.is_deleted:
            return
        self.is_deleted = True
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(MessageDeleted(message_id=str(self.id)))

    def add_reaction(self, user_id: Id, emoji: ReactionEmoji) -> None:
        if any(r.user_id == user_id and r.emoji == emoji for r in self.reactions):
            raise DuplicateReactionException()
        reaction = Reaction(user_id=user_id, emoji=emoji)
        self.reactions.append(reaction)
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MessageReactionAdded(message_id=str(self.id), user_id=str(user_id), emoji=str(emoji))
        )

    def remove_reaction(self, user_id: Id, emoji: ReactionEmoji) -> None:
        self.reactions = [
            r for r in self.reactions
            if not (r.user_id == user_id and r.emoji == emoji)
        ]
        self.updated_at = datetime.now(tz=timezone.utc)
        self._register_event(
            MessageReactionRemoved(message_id=str(self.id), user_id=str(user_id), emoji=str(emoji))
        )

    def add_attachment(self, attachment: Attachment) -> None:
        self.attachments.append(attachment)
        self.updated_at = datetime.now(tz=timezone.utc)

    def remove_attachment(self, attachment_id: Id) -> None:
        self.attachments = [a for a in self.attachments if a.id != attachment_id]
        self.updated_at = datetime.now(tz=timezone.utc)
