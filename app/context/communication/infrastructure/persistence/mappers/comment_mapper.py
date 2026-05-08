from __future__ import annotations

from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.rich_text_format import RichTextFormat
from app.shared.domain.value_objects.rich_text_vo import RichText
from app.shared.domain.value_objects.url_vo import Url
from app.shared.infrastructure.persistence.sqlalchemy_base_mapper import BaseMapper

from app.context.communication.domain.aggregates.comment import Comment
from app.context.communication.domain.entities.attachment import Attachment
from app.context.communication.domain.entities.reaction import Reaction
from app.context.communication.domain.value_objects.attachment_type import (
    AttachmentType,
)
from app.context.communication.domain.value_objects.comment_target_type import (
    CommentTargetType,
)
from app.context.communication.domain.value_objects.reaction_emoji import ReactionEmoji
from app.context.communication.infrastructure.persistence.orm_models.comment_orm import (
    CommentAttachmentORM,
    CommentORM,
    CommentReactionORM,
)


class CommentMapper(BaseMapper[Comment, CommentORM]):
    """Data Mapper: Comment ↔ CommentORM."""

    def to_domain(self, orm_model: CommentORM) -> Comment:
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

        return Comment(
            id=self._map_id(orm_model.id),
            author_id=self._map_id(orm_model.author_id),
            target_type=CommentTargetType(orm_model.target_type),
            target_id=self._map_id(orm_model.target_id),
            content=content,
            parent_comment_id=(
                self._map_id(orm_model.parent_comment_id)
                if orm_model.parent_comment_id
                else None
            ),
            attachments=attachments,
            reactions=reactions,
            is_pinned=orm_model.is_pinned,
            is_system=orm_model.is_system,
            is_deleted=orm_model.is_deleted,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, aggregate: Comment) -> CommentORM:
        orm = CommentORM(
            id=self._map_uuid(aggregate.id),
            author_id=self._map_uuid(aggregate.author_id),
            target_type=aggregate.target_type.value,
            target_id=self._map_uuid(aggregate.target_id),
            parent_comment_id=(
                self._map_uuid(aggregate.parent_comment_id)
                if aggregate.parent_comment_id
                else None
            ),
            content=aggregate.content.content if aggregate.content else None,
            content_format=(
                aggregate.content.format.value if aggregate.content else "markdown"
            ),
            is_pinned=aggregate.is_pinned,
            is_system=aggregate.is_system,
            is_deleted=aggregate.is_deleted,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
        )
        orm.reactions = [self._reaction_to_orm(r, aggregate.id) for r in aggregate.reactions]
        orm.attachments = [
            self._attachment_to_orm(a, aggregate.id) for a in aggregate.attachments
        ]
        return orm

    def _reaction_to_orm(self, reaction: Reaction, comment_id: Id) -> CommentReactionORM:
        return CommentReactionORM(
            id=self._map_uuid(reaction.id),
            comment_id=self._map_uuid(comment_id),
            user_id=self._map_uuid(reaction.user_id),
            emoji=str(reaction.emoji),
            reaction_created_at=reaction.created_at,
        )

    def _attachment_to_orm(
        self, attachment: Attachment, comment_id: Id
    ) -> CommentAttachmentORM:
        return CommentAttachmentORM(
            id=self._map_uuid(attachment.id),
            comment_id=self._map_uuid(comment_id),
            file_id=self._map_uuid(attachment.file_id),
            attachment_type=attachment.attachment_type.value,
            name=attachment.name,
            size_bytes=attachment.size_bytes,
            url=str(attachment.url) if attachment.url else None,
            preview_url=str(attachment.preview_url) if attachment.preview_url else None,
            attachment_created_at=attachment.created_at,
        )
