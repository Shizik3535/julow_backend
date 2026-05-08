from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.shared.domain.value_objects.url_vo import Url
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.communication.domain.aggregates.message import Message
from app.context.communication.domain.entities.attachment import Attachment
from app.context.communication.domain.entities.reaction import Reaction
from app.context.communication.domain.value_objects.attachment_type import (
    AttachmentType,
)
from app.context.communication.domain.value_objects.message_type import MessageType
from app.context.communication.domain.value_objects.reaction_emoji import ReactionEmoji
from app.context.communication.infrastructure.persistence.orm_models.message_orm import (
    MessageAttachmentORM,
    MessageORM,
    MessageReactionORM,
)


class MessageMapper(BaseMapper[Message, MessageORM]):
    """Data Mapper: Message ↔ MessageORM."""

    def to_domain(self, orm_model: MessageORM) -> Message:
        content: RichText | None = None
        if orm_model.content is not None:
            content = RichText(
                content=orm_model.content,
                format=RichTextFormat(orm_model.content_format),
            )

        reactions = [
            Reaction(
                id=self._map_id(r.id),
                user_id=self._map_id(r.user_id),
                emoji=ReactionEmoji(value=r.emoji),
                created_at=r.reaction_created_at,
            )
            for r in (orm_model.reactions or [])
        ]
        attachments = [
            Attachment(
                id=self._map_id(a.id),
                file_id=self._map_id(a.file_id),
                url=Url(value=a.url) if a.url else None,
                attachment_type=AttachmentType(a.attachment_type),
                name=a.name,
                size_bytes=a.size_bytes,
                preview_url=Url(value=a.preview_url) if a.preview_url else None,
                created_at=a.attachment_created_at,
            )
            for a in (orm_model.attachments or [])
        ]

        return Message(
            id=self._map_id(orm_model.id),
            chat_id=self._map_id(orm_model.chat_id),
            thread_id=(
                self._map_id(orm_model.thread_id) if orm_model.thread_id else None
            ),
            sender_id=self._map_id(orm_model.sender_id),
            content=content,
            message_type=MessageType(orm_model.message_type),
            attachments=attachments,
            reactions=reactions,
            is_edited=orm_model.is_edited,
            is_deleted=orm_model.is_deleted,
            reply_to_id=(
                self._map_id(orm_model.reply_to_id) if orm_model.reply_to_id else None
            ),
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Message) -> MessageORM:
        orm = MessageORM(
            id=self._map_uuid(aggregate.id),
            chat_id=self._map_uuid(aggregate.chat_id),
            thread_id=(
                self._map_uuid(aggregate.thread_id) if aggregate.thread_id else None
            ),
            sender_id=self._map_uuid(aggregate.sender_id),
            reply_to_id=(
                self._map_uuid(aggregate.reply_to_id) if aggregate.reply_to_id else None
            ),
            content=aggregate.content.content if aggregate.content else None,
            content_format=(
                aggregate.content.format.value if aggregate.content else "markdown"
            ),
            message_type=aggregate.message_type.value,
            is_edited=aggregate.is_edited,
            is_deleted=aggregate.is_deleted,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.reactions = [
            self._reaction_to_orm(r, aggregate.id) for r in aggregate.reactions
        ]
        orm.attachments = [
            self._attachment_to_orm(a, aggregate.id) for a in aggregate.attachments
        ]
        return orm

    def _reaction_to_orm(
        self, reaction: Reaction, message_id: Id
    ) -> MessageReactionORM:
        return MessageReactionORM(
            id=self._map_uuid(reaction.id),
            message_id=self._map_uuid(message_id),
            user_id=self._map_uuid(reaction.user_id),
            emoji=str(reaction.emoji),
            reaction_created_at=reaction.created_at,
        )

    def _attachment_to_orm(
        self, attachment: Attachment, message_id: Id
    ) -> MessageAttachmentORM:
        return MessageAttachmentORM(
            id=self._map_uuid(attachment.id),
            message_id=self._map_uuid(message_id),
            file_id=self._map_uuid(attachment.file_id),
            attachment_type=attachment.attachment_type.value,
            name=attachment.name,
            size_bytes=attachment.size_bytes,
            url=str(attachment.url) if attachment.url else None,
            preview_url=str(attachment.preview_url) if attachment.preview_url else None,
            attachment_created_at=attachment.created_at,
        )
